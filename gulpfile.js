var gulp = require('gulp');
var concat = require('gulp-concat');
var jshint = require('gulp-jshint');
var minifyHTML = require('gulp-minify-html');
var terser = require('gulp-terser');
var rename = require('gulp-rename');
var newer = require('gulp-newer');
var less = require('gulp-less');
var cleanCSS = require('gulp-clean-css');
var sourcemaps = require('gulp-sourcemaps');
var merge = require('merge-stream');
var { spawn } = require('child_process');

// -------------------
// Lint JS
// -------------------
gulp.task('lint', gulp.series(function(done) {
  return gulp.src(['scripts/default.js'])
    .pipe(jshint({ esversion: 6 })) // allow ES6
    .pipe(jshint.reporter('default'));
  done();
}));

// -------------------
// Compile JS
// -------------------
gulp.task('scripts', gulp.series(function(done) {
  return gulp.src([
      'scripts/jquery-3.4.1.min.js',
      'scripts/jquery-ui.1.11.4.min.js',
      'scripts/bootstrap.min.js',
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
gulp.task('styles', function() {
  var uncompressed = gulp.src('styles/default.less')
    .pipe(sourcemaps.init())
    .pipe(less().on('error', function(err) {
      console.error(err.message);
      this.emit('end');
    }))
    .pipe(rename('all.css'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('styles'));

  var compressed = gulp.src('styles/default.less')
    .pipe(less().on('error', function(err) {
      console.error(err.message);
      this.emit('end');
    }))
    .pipe(cleanCSS())
    .pipe(rename('all.min.css'))
    .pipe(gulp.dest('styles'));

  return merge(uncompressed, compressed);
});

// -------------------
// Optimize HTML
// -------------------
gulp.task('optimize-html', gulp.series(function(done) {
  return gulp.src('_site/**/*.html')
    .pipe(newer('_site')) // only process newer files
    .pipe(minifyHTML({ quotes: true }))
    .pipe(gulp.dest('_site'));
  done();
}));

// -------------------
// Serve Jekyll (_site) and filter .well-known errors
// -------------------
gulp.task('serve', function(done) {
  const jekyll = spawn('bundle', ['exec', 'jekyll', 'serve'], { stdio: ['ignore', 'pipe', 'pipe'] });

  jekyll.stdout.on('data', function(data) {
    let lines = data.toString().split('\n').filter(line => !line.includes('.well-known/appspecific'));
    lines.forEach(line => console.log(line));
  });

  jekyll.stderr.on('data', function(data) {
    let lines = data.toString().split('\n').filter(line => !line.includes('.well-known/appspecific'));
    lines.forEach(line => console.error(line));
  });

  jekyll.on('close', function(code) {
    console.log(`Jekyll exited with code ${code}`);
  });

  done();
});

// -------------------
// Watch files
// -------------------
gulp.task('watch', function () {
  gulp.watch([
    'scripts/default.js',
    'scripts/jquery-3.4.1.min.js',
    'scripts/jquery-ui.1.11.4.min.js',
    'scripts/bootstrap.min.js',
    '!scripts/all.js',       // ignore output
    '!scripts/all.min.js'    // ignore output
  ], gulp.series('scripts'));

  gulp.watch('styles/**/*.less', gulp.series('styles'));
  gulp.watch('_site/**/*.html', gulp.series('optimize-html'));
});

// -------------------
// Default task
// -------------------
gulp.task('default', gulp.series('lint', 'scripts', 'styles', 'optimize-html', 'serve', function(done) {
  done();
}));
