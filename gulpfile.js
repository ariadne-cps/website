var gulp = require('gulp');
var ftp = require('vinyl-ftp');
var gutil = require('gulp-util');
var minimist = require('minimist');
var args = minimist(process.argv.slice(2));

gulp.task('deploy', function() {
  var remotePath = '/www.ariadne-cps.org/';
  var conn = ftp.create({
    host: 'ftp.ariadne-cps.org',
    user: args.user,
    password: args.password,
    parallel: 1,
    maxConnections: 1,
    log: gutil.log
  });

  return gulp.src(['public/**/*'], { buffer: false })
    .pipe(conn.newer(remotePath))
    .pipe(conn.dest(remotePath));
});
