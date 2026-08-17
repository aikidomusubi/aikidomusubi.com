var gulp       = require('gulp');
var concat     = require('gulp-concat');
var jshint     = require('gulp-jshint');
var htmlmin    = require('gulp-htmlmin');
var terser     = require('gulp-terser');
var rename     = require('gulp-rename');
var newer      = require('gulp-newer');
var less       = require('gulp-less');
var cleanCSS   = require('gulp-clean-css');
var postcss    = require('gulp-postcss');
var autoprefixer = require('autoprefixer');
var { spawn }  = require('child_process');

// -------------------
// Lint JS
// -------------------
gulp.task('lint', gulp.series(function(done) {
  return gulp.src(['scripts/default.js'])
    .pipe(jshint({ esversion: 6 }))
    .pipe(jshint.reporter('default'));
  done();
}));

// -------------------
// Compile JS
// -------------------
gulp.task('scripts', gulp.series(function(done) {
  return gulp.src([
      'scripts/bootstrap.bundle.min.js',
      'scripts/default.js'
    ])
    .pipe(concat('all.js'))
    .pipe(gulp.dest('scripts'))
    .pipe(rename('all.min.js'))
    .pipe(terser())
    .pipe(gulp.dest('scripts'));
  done();
}));

// -------------------
// Compile LESS to CSS
// -------------------
// Emits styles/all.min.css only.
//
// This task used to build an unminified styles/all.css alongside it through
// a second stream wrapped in gulp-sourcemaps. That stream had been failing
// silently — all.css was months stale, still carrying vendor prefixes that
// had already been deleted from the source — because gulp-sourcemaps 2.x
// does not work under Gulp 5. Nothing consumed the file (it is not served
// and it is excluded from the Jekyll build), so the second stream is gone
// rather than repaired, which also drops two unmaintained dependencies.
gulp.task('styles', function() {
  return gulp.src('styles/default.less')
    .pipe(less().on('error', function(err) {
      console.error(err.message);
      this.emit('end');
    }))
    .pipe(postcss([autoprefixer()]))
    .pipe(cleanCSS())
    .pipe(rename('all.min.css'))
    .pipe(gulp.dest('styles'));
});

// -------------------
// Drop unused CSS
//
// Bootstrap is ~235 KB of the 327 KB bundle and this site uses a fraction of
// it. Purging takes all.min.css to ~157 KB, which is ~20 KB per page once
// brotli has had it.
//
// Content is the BUILT SITE, not the templates, and that is not a detail.
// Kramdown generates <blockquote>, <table>, <em> and friends from Markdown
// punctuation, so those tag names appear nowhere in the sources — purging
// against templates silently dropped the blockquote rules on the cookie
// policy pages. _site is what actually ships; purge against that.
//
// The extractor only accepts class-shaped tokens. The default one reads
// ordinary prose as class names, which is why an earlier attempt at this
// saved almost nothing. The safelist covers what no static analysis can see:
// classes that only exist once JS has run — Bootstrap's .show/.collapsing
// states, everything FullCalendar builds at runtime, GLightbox, and the
// cookie banner's .is-open.
//
// Run order matters: gulp styles -> jekyll build -> gulp purge -> commit.
// Getting it wrong is visible rather than silent — a class purged before it
// was used simply looks broken locally, since the committed bundle is what
// the dev server serves.
// -------------------
gulp.task('purge', function() {
  // v6 exports the plugin as module.exports itself, not on .default.
  var purgecss = require('@fullhuman/postcss-purgecss');
  var fs = require('fs');

  if (!fs.existsSync('_site') || fs.readdirSync('_site').length < 5) {
    throw new Error('purge needs a built _site — run jekyll build first');
  }

  return gulp.src('styles/all.min.css')
    .pipe(postcss([purgecss({
      content: [
        '_site/**/*.html',
        'scripts/default.js',
        'scripts/schedule.js',
        'scripts/calendar.js',
        'scripts/glightbox.min.js',
        'plugins/fullcalendar-4.3.1/packages/*/main.min.js'
      ],
      defaultExtractor: function(content) {
        return content.match(/[\w-/:%.]+(?<!:)/g) || [];
      },
      safelist: {
        // /^tt-/ covers the timetable. Its tabs, now-line and calendar links
        // are built by scripts/schedule.js and never appear in the built HTML,
        // and neither do the data-* states (data-active, data-today,
        // data-narrow, data-short, data-tiny) the stylesheet keys off.
        standard: [/^tt-/, /^timetable/, /^cal-/, /^calendar/, /^fc-/, /^gl/, /^is-/, /^cookie-/, /^navbar/, /^dropdown/,
                   /^collaps/, /^modal/, /^offcanvas/, /^carousel/, /^tooltip/,
                   /^popover/, /^toast/, 'show', 'showing', 'hide', 'hiding',
                   'fade', 'active', 'disabled', 'open', 'table-bordered',
                   'sticky-top', 'fixed-bottom'],
        deep: [/^fc-/, /^gl/, /^modal/, /^tt-/, /^cal-/],
        greedy: [/^fc/, /^gl/]
      }
    })]))
    .pipe(cleanCSS())
    .pipe(gulp.dest('styles'));
});

// -------------------
// Page-specific JS
//
// The timetable script is loaded only on the training-schedule page, so it
// stays out of all.min.js rather than costing every other page ~3 KB for
// behaviour they never use.
// -------------------
gulp.task('schedule-js', function() {
  return gulp.src('scripts/schedule.js')
    .pipe(terser())
    .pipe(rename('schedule.min.js'))
    .pipe(gulp.dest('scripts'));
});

gulp.task('calendar-js', function() {
  return gulp.src('scripts/calendar.js')
    .pipe(terser())
    .pipe(rename('calendar.min.js'))
    .pipe(gulp.dest('scripts'));
});

// -------------------
// Minify HTML
// -------------------
gulp.task('optimize-html', gulp.series(function(done) {
  return gulp.src('_site/**/*.html')
    .pipe(newer('_site'))
    .pipe(htmlmin({ collapseWhitespace: true, removeComments: true, minifyJS: true, minifyCSS: true }))
    .pipe(gulp.dest('_site'));
  done();
}));

// -------------------
// Watch files
// -------------------
gulp.task('watch', function () {
  gulp.watch([
    'scripts/default.js',
    'scripts/bootstrap.bundle.min.js',
    '!scripts/all.js',
    '!scripts/all.min.js'
  ], gulp.series('scripts'));

  gulp.watch('styles/**/*.less', gulp.series('styles'));
  gulp.watch('_site/**/*.html', gulp.series('optimize-html'));
});

// -------------------
// Default task
// -------------------
gulp.task('default', gulp.series('lint', 'scripts', 'styles', 'optimize-html', function(done) {
  done();
}));
