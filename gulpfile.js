var gulp = require('gulp');

var concat = require('gulp-concat');
var jshint = require('gulp-jshint');
var minifyHTML = require('gulp-minify-html');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');

gulp.task('lint', gulp.series(function(done) {
  return gulp.src(['scripts/default.js'])
  .pipe(jshint())
  .pipe(jshint.reporter('default'));
  done();
}));

gulp.task('scripts', gulp.series(function(done) {
  return gulp.src(['scripts/jquery-*.min.js', 'scripts/jquery-ui-*.min.js', 'scripts/bootstrap.min.js', 'scripts/default.js'])
  .pipe(concat('all.js'))
  .pipe(gulp.dest('scripts'))
  .pipe(rename('all.min.js'))
  .pipe(uglify())
  .pipe(gulp.dest('scripts'));
  done();
}));

gulp.task('optimize-html', gulp.series(function(done) {
  return gulp.src('_site/**/*.html')
  .pipe(minifyHTML({
    quotes: true
  }))
  .pipe(gulp.dest('_site/'));
  done();
}));

gulp.task('watch', function () {
  gulp.watch('scripts/**/*.js', gulp.series('scripts')); // Watch JavaScript files
  gulp.watch('_site/**/*.html', gulp.series('optimize-html')); // Watch HTML files
});

gulp.task('default', gulp.series('lint', 'scripts', 'optimize-html', function(done) {
  done();
}));
