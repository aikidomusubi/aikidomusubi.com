// =============================================================================
// Aikido Musubi — asset pipeline
//
// GitHub Pages runs Jekyll and nothing else, so whatever is committed in
// styles/ and scripts/ is exactly what ships. Every task here writes into the
// source tree, and the compiled output is committed alongside the source.
//
// THE ONE COMMAND THAT MATTERS
//
//     npx gulp build
//
// It runs the full sequence in the only order that is correct, and refuses to
// finish if the CSS bundle is not the purged one. Run it before committing and
// the pipeline cannot be left half-applied.
//
// During development use `npx gulp watch`, which is deliberately fast and
// deliberately NOT correct: it leaves all.min.css unpurged so that every class
// is available while you are still adding markup. `build` puts that right.
// =============================================================================

var gulp         = require('gulp');
var concat       = require('gulp-concat');
var jshint       = require('gulp-jshint');
var terser       = require('gulp-terser');
var rename       = require('gulp-rename');
var less         = require('gulp-less');
var cleanCSS     = require('gulp-clean-css');
var postcss      = require('gulp-postcss');
var autoprefixer = require('autoprefixer');
var fs           = require('fs');
var path         = require('path');
var { spawn }    = require('child_process');

// The scripts this repo authors. Vendor bundles (bootstrap, glightbox) and
// build output (*.min.js) is deliberately absent — it is not ours to lint and
// not ours to rebuild. `all.js` used to be listed here too; it was a leftover
// concatenation artefact that no task produced and no page loaded, and it has
// been deleted.
var AUTHORED_SCRIPTS = [
  'scripts/default.js',
  'scripts/schedule.js',
  'scripts/calendar.js',
  'scripts/fees.js',
  'scripts/press.js',
  'scripts/gallery.js',
  'scripts/seminars.js',
  'scripts/nav.js',
  'scripts/ura.js',
  'scripts/notfound.js',
  'scripts/glossary.js',
  'scripts/resources.js'
];

// Everything in AUTHORED_SCRIPTS except default.js, which is concatenated into
// the core bundle instead of shipping as its own file.
var PAGE_SCRIPTS = AUTHORED_SCRIPTS.filter(function (f) {
  return f !== 'scripts/default.js';
});

function lessStream(glob) {
  return gulp.src(glob)
    .pipe(less().on('error', function (err) {
      // FAIL. This used to print the message and call `this.emit('end')`, which
      // ends the stream cleanly: gulp reported success, the previous
      // all.min.css stayed on disk, and `check-css` — which only measures how
      // purged the file is — said "css ok". A stray edit broke nav.less and
      // every stylesheet change for the rest of the session compiled into
      // nothing while the build claimed to be green. A compile error is not a
      // warning.
      console.error('\n  LESS FAILED — the bundle on disk is STALE\n  ' +
                    err.message + '\n');
      this.emit('error', err);
    }))
    .pipe(postcss([autoprefixer()]))
    .pipe(cleanCSS());
}

function requireSite() {
  if (!fs.existsSync('_site') || fs.readdirSync('_site').length < 5) {
    throw new Error('needs a built _site — run `npx gulp jekyll` first');
  }
}

// -----------------------------------------------------------------------------
// Lint
// -----------------------------------------------------------------------------
// Options live in .jshintrc, where each non-default setting carries a comment
// explaining which pattern in this codebase it exists for.
gulp.task('lint', function () {
  return gulp.src(AUTHORED_SCRIPTS)
    .pipe(jshint('.jshintrc'))
    .pipe(jshint.reporter('default'))
    .pipe(jshint.reporter('fail'));
});

// -----------------------------------------------------------------------------
// Scripts
// -----------------------------------------------------------------------------
// The core bundle, on every page.
//
// bootstrap.bundle.min.js used to lead this list — 79 KB for exactly two
// behaviours, the navbar dropdown and its collapse, both of which now live in
// scripts/nav.js at about 1.5 KB. Lighthouse reported 69 KiB of the old bundle
// as unused. Nothing else on the site ever called a Bootstrap component: the
// only `data-bs-*` attributes anywhere were in _includes/navigation.html.
gulp.task('scripts', function () {
  return gulp.src(['scripts/default.js'])
    .pipe(concat('all.min.js'))
    .pipe(terser())
    .pipe(gulp.dest('scripts'));
});

// One bundle per page-specific script, loaded only by the page that needs it.
// These used to be seven near-identical hand-written tasks, and adding a script
// meant remembering to add an eighth — press.min.js went stale exactly that way.
gulp.task('page-scripts', function () {
  return gulp.src(PAGE_SCRIPTS)
    .pipe(terser())
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest('scripts'));
});

// -----------------------------------------------------------------------------
// Styles
// -----------------------------------------------------------------------------
// The core bundle. Unpurged at this point — `purge` below is what trims it.
gulp.task('styles', function () {
  return lessStream('styles/default.less')
    .pipe(rename('all.min.css'))
    .pipe(gulp.dest('styles'));
});

// One stylesheet per page component, loaded only on the page that uses it.
// Keeping these in the core bundle meant every visitor downloaded the timetable
// grid and the fee tables before the home page could paint.
gulp.task('page-styles', function () {
  return lessStream('styles/page-*.less')
    .pipe(rename(function (path) {
      path.basename = path.basename.replace(/^page-/, '') + '.min';
    }))
    .pipe(gulp.dest('styles'));
});

// -----------------------------------------------------------------------------
// Jekyll
// -----------------------------------------------------------------------------
// RUBYOPT is required: the shell has an empty LANG, so without it the Sass
// converter treats files as US-ASCII and the build dies on the first non-ASCII
// character.
gulp.task('jekyll', function (done) {
  var proc = spawn('bundle', ['exec', 'jekyll', 'build'], {
    stdio: 'inherit',
    env: Object.assign({}, process.env, { RUBYOPT: '-E utf-8:utf-8' })
  });
  proc.on('close', function (code) {
    done(code === 0 ? null : new Error('jekyll build failed (' + code + ')'));
  });
});

// -----------------------------------------------------------------------------
// Drop unused CSS
// -----------------------------------------------------------------------------
// Bootstrap dominates the core bundle and this site uses a fraction of it.
// Purging takes all.min.css from ~300 KB to ~113 KB.
//
// Content is the BUILT SITE, not the templates, and that is not a detail.
// Kramdown generates <blockquote>, <table>, <em> and friends from Markdown
// punctuation, so those tag names appear nowhere in the sources — purging
// against templates silently dropped the blockquote rules on the cookie policy
// pages.
//
// The extractor only accepts class-shaped tokens. The default one reads
// ordinary prose as class names, which is why an earlier attempt at this saved
// almost nothing. The safelist covers what no static analysis can see: classes
// that exist only once JS has run.
function purgeOptions() {
  var purgecss = require('@fullhuman/postcss-purgecss');
  var glob = require('glob');

  // THE STYLE BLOCKS ARE STRIPPED FIRST, and that is not optional.
  //
  // The CSS is inlined into every page, and the extractor accepts anything
  // class-shaped — so reading the built HTML as-is would find every selector
  // in the bundle's own copy of itself and conclude that all of it is in use.
  // Purging would silently become a no-op and the 51 KB bundle would ship at
  // the ~190 KB it starts as, with the check that guards it agreeing.
  var pages = glob.sync('_site/**/*.html').map(function (f) {
    return { raw: fs.readFileSync(f, 'utf8').replace(/<style[\s\S]*?<\/style>/gi, ''),
             extension: 'html' };
  });

  return purgecss({
    content: pages.concat(AUTHORED_SCRIPTS, ['scripts/glightbox.min.js']),
    defaultExtractor: function (content) {
      return content.match(/[\w-/:%.]+(?<!:)/g) || [];
    },
    safelist: {
      // /^tt-/ covers the timetable: its tabs, now-line and calendar links are
      // built by scripts/schedule.js and never appear in the built HTML, and
      // neither do the data-* states the stylesheet keys off.
      // Only what a script actually creates at runtime. The Bootstrap component
      // families that used to be listed here — navbar, dropdown, collapse,
      // modal, offcanvas, carousel, tooltip, popover, toast, plus sticky-top,
      // table-bordered and fixed-bottom — were kept safe because
      // bootstrap.bundle.js applied them at runtime where no static analysis
      // could see them. That script is gone, and a check across the built site
      // found all twelve on zero pages, so the safelist was preserving CSS for
      // components the site no longer has.
      standard: [/^tt-/, /^timetable/, /^cal-/, /^calendar/, /^seminar/, /^gx-/,
                 /^pv-/, /^fee-/, /^vn-/, /^vs-/, /^ct-/, /^gl/, /^is-/,
                 /^cookie-/, /^nv-/, /^ft-/, /^ab-/, /^cl-/,
                 'show', 'showing', 'hide', 'hiding', 'fade', 'active',
                 'disabled', 'open'],
      deep: [/^gl/, /^tt-/, /^cal-/],
      greedy: [/^gl/]
    }
  });
}

gulp.task('purge', function () {
  requireSite();
  return gulp.src('styles/all.min.css')
    .pipe(postcss([purgeOptions()]))
    .pipe(cleanCSS())
    .pipe(gulp.dest('styles'))
    // _site holds a copy Jekyll made before the purge. Refreshing it here means
    // the dev server serves what will ship without a second 30-second build.
    .pipe(gulp.dest('_site/styles'));
});

// Fails the build if all.min.css is not the purged one. `gulp watch` rewrites
// it unpurged on every LESS edit, which is right for development and wrong for
// a commit — this is what stops the unpurged bundle reaching production.
// It re-purges in memory and compares, so there is no size threshold to
// maintain and no way for the check to drift from the task it is checking.
gulp.task('check-css', function (done) {
  requireSite();
  var postcssLib = require('postcss');
  var current = fs.readFileSync('styles/all.min.css', 'utf8');
  postcssLib([purgeOptions()]).process(current, { from: undefined })
    .then(function (result) {
      var saving = current.length - result.css.length;
      if (saving > current.length * 0.02) {
        done(new Error(
          'styles/all.min.css is not purged — ' + Math.round(saving / 1024) +
          ' KB of unused CSS is still in it. Run `npx gulp build`.'));
      } else {
        console.log('    css ok — ' + Math.round(current.length / 1024) + ' KB, purged');
        done();
      }
    })
    .catch(done);
});

// -----------------------------------------------------------------------------
// Nothing but built assets in the output
// -----------------------------------------------------------------------------
// `exclude:` in _config.yml keeps Gulp's inputs out of _site. It used to name
// every source file individually and it drifted every single time one was
// added: eleven files — 65 KB of .less and unminified .js — were being deployed
// to production before anyone noticed. It uses globs now, and this makes sure
// they keep working, because a silent leak is exactly the kind of thing nobody
// looks for twice.
gulp.task('check-assets', function (done) {
  requireSite();
  var leaked = [];

  ['_site/styles', '_site/scripts'].forEach(function (dir) {
    if (!fs.existsSync(dir)) return;
    fs.readdirSync(dir).forEach(function (f) {
      var isSource = /\.less$/.test(f) || (/\.js$/.test(f) && !/\.min\.js$/.test(f));
      if (isSource) leaked.push(dir + '/' + f);
    });
  });

  // And the other direction. Excluding `scripts/*.js` to stop the sources
  // leaking also excluded the bundles — Jekyll's `include:` does not rescue a
  // glob-excluded file — and the whole site shipped with no scripts while this
  // check happily reported "no sources in _site". A guard that only looks for
  // what should be absent cannot see what has gone missing.
  var expected = PAGE_SCRIPTS.map(function (f) {
    return path.basename(f, '.js') + '.min.js';
  }).concat(['all.min.js', 'glightbox.min.js']);
  var missing = expected.filter(function (f) {
    return !fs.existsSync(path.join('_site', 'scripts', f));
  });

  if (leaked.length) {
    done(new Error(
      'source files reached _site — add a matching glob to `exclude:` in ' +
      '_config.yml:\n    ' + leaked.join('\n    ')));
  } else if (missing.length) {
    done(new Error(
      'built scripts did NOT reach _site — check `exclude:` in _config.yml:' +
      '\n    ' + missing.join('\n    ')));
  } else {
    console.log('    assets ok — no sources in _site, ' +
                expected.length + ' bundles present');
    done();
  }
});

// -----------------------------------------------------------------------------
// QA
// -----------------------------------------------------------------------------
// The standing checks — structure, headings, links, sitemap, accessibility,
// SEO tags, build hygiene, dead code, page weight, lastmod. See tools/qa.py for
// what each one is for and why it exists.
//
// Deliberately NOT part of `build`: it reads the built site, so it has to run
// after it, and keeping it separate means a failing check reports everything it
// found instead of stopping the pipeline at the first problem. Run it before
// calling anything done.
gulp.task('qa', function (done) {
  requireSite();
  var proc = spawn('python3', ['tools/qa.py'], { stdio: 'inherit' });
  proc.on('close', function (code) {
    done(code === 0 ? null : new Error('QA reported failures'));
  });
});

// -----------------------------------------------------------------------------
// Watch
// -----------------------------------------------------------------------------
// Fast, not correct: no Jekyll, no purge. The dev server serves the unpurged
// bundle, so a class you have only just written is already available instead of
// looking broken until the next purge.
gulp.task('watch', function () {
  gulp.watch('scripts/default.js', gulp.series('scripts'));
  gulp.watch(PAGE_SCRIPTS, gulp.series('page-scripts'));
  gulp.watch('styles/**/*.less', gulp.series('styles', 'page-styles'));
  console.log('    watching — run `npx gulp build` before committing');
});

// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// stamp — the ?v= tokens, derived from the files they version
// -----------------------------------------------------------------------------
// Every asset URL used to carry a hand-written `?v=N`, twenty-two of them
// across header.html and footer.html, each needing a bump whenever its file
// changed. They drifted, exactly as the excludes and the safelist did before
// them: `ura.min.js` changed with `?v=5` left alone, so returning visitors ran
// the old script, and `ura.min.css` was `?v=3` on the stylesheet and `?v=5` on
// its own preload — two cache entries for one file, which makes the preload a
// second download rather than a head start.
//
// The token is now the first eight characters of the file's SHA-1, published
// as `_data/assets.yml` and read by the templates. It changes when and only
// when the file does, so it cannot drift and cannot invalidate a cache for
// nothing.
//
// It runs before `jekyll` and therefore hashes `all.min.css` unpurged. That is
// fine and deliberate: the token has to *change with* the content, not equal
// it, and the unpurged bundle is a pure function of the sources.
gulp.task('stamp', function (done) {
  var crypto = require('crypto');
  var files = []
    .concat(glob('scripts/*.min.js'))
    .concat(glob('styles/*.min.css'))
    .sort();
  var rows = files.map(function (f) {
    var h = crypto.createHash('sha1').update(fs.readFileSync(f)).digest('hex').slice(0, 8);
    return '"' + path.basename(f) + '": ' + h;
  });
  var body = '# Generated by `gulp stamp` — do not edit.\n' +
             '# Cache-busting tokens: the first eight hex of each bundle\'s SHA-1.\n' +
             rows.join('\n') + '\n';
  // An empty map is worse than no map: every `?v=` in every template would
  // render blank, which still works but silently throws away the cache
  // busting this task exists to provide.
  if (rows.length < 10) {
    done(new Error('stamp found only ' + rows.length + ' bundles — expected the '
      + 'compiled scripts and styles. Run `gulp scripts page-scripts styles '
      + 'page-styles` first.'));
    return;
  }
  fs.writeFileSync('_data/assets.yml', body);
  console.log('    stamped ' + rows.length + ' bundles');
  done();
});

function glob(pattern) {
  var dir = pattern.split('/')[0];
  var rx = new RegExp('^' + pattern.split('/')[1].replace(/\./g, '\\.').replace(/\*/g, '.*') + '$');
  if (!fs.existsSync(dir)) { return []; }
  return fs.readdirSync(dir).filter(function (f) { return rx.test(f); })
    .map(function (f) { return dir + '/' + f; });
}

// Build
// -----------------------------------------------------------------------------
// The whole pipeline in the only order that works: compile, build the site,
// purge against what was built, then verify.
gulp.task('build', gulp.series(
  'lint', 'scripts', 'page-scripts', 'styles', 'page-styles',
  'stamp', 'jekyll', 'purge', 'check-css', 'check-assets'
));

gulp.task('default', gulp.series('build'));
