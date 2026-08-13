var gulp       = require('gulp');
var concat     = require('gulp-concat');
var jshint     = require('gulp-jshint');
var htmlmin    = require('gulp-htmlmin');
var terser     = require('gulp-terser');
var rename     = require('gulp-rename');
var newer      = require('gulp-newer');
var less       = require('gulp-less');
var cleanCSS   = require('gulp-clean-css');
var sourcemaps = require('gulp-sourcemaps');
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
      'scripts/jquery-3.7.1.min.js',
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
gulp.task('styles', function() {
  var uncompressed = gulp.src('styles/default.less')
    .pipe(sourcemaps.init())
    .pipe(less().on('error', function(err) {
      console.error(err.message);
      this.emit('end');
    }))
    .pipe(postcss([autoprefixer()]))
    .pipe(rename('all.css'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('styles'));

  var compressed = gulp.src('styles/default.less')
    .pipe(less().on('error', function(err) {
      console.error(err.message);
      this.emit('end');
    }))
    .pipe(postcss([autoprefixer()]))
    .pipe(cleanCSS())
    .pipe(rename('all.min.css'))
    .pipe(gulp.dest('styles'));

  return require('merge-stream')(uncompressed, compressed);
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
    'scripts/jquery-3.7.1.min.js',
    'scripts/bootstrap.min.js',
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
