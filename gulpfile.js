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
