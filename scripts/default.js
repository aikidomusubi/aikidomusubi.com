/* jshint esversion: 6 */

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

  function hiddenCode() {

    var kkeys = [];
    var konami = '38,38,40,40,37,39,37,39,66,65'; // up, up, down, down, left, right, left, right, b, a

    ////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////

    $(document).keydown(function(e) {
      kkeys.push(e.keyCode);
      if (kkeys.toString().indexOf(konami) >= 0) {
        kkeys = [];
        window.location.href = 'https://youtu.be/UzdDAd9EBOI';
      }
    });
  }

  function revealContent() {

    $('body').removeClass('invisible').addClass('fadeIn');
  }

  function parallaxHeader() { // https://codepen.io/theaftermath87/pen/mJqywj

    var w=window,
    d=document,
    e=d.documentElement,
    g=d.getElementsByTagName('body')[0],
    x=w.innerWidth||e.clientWidth||g.clientWidth,
    y=w.innerHeight||e.clientHeight||g.clientHeight;

    var $falseHeader = $('.falseHeader');
    var $shadower = $('.shadower');
    var $fixedHead = $('.fixedHead');
    var stickyHeight = $falseHeader.offset().top;

    if (x >= 992 && x <= 1919 ) {

      $fixedHead.css({
        backgroundPosition: '50% -215' + 'px'
      });
    } else if (x >= 1920 && y <= 1199 ) {

      $fixedHead.css({
        backgroundPosition: '50% -430' + 'px'
      });
    } else if (x >= 1920 && y >= 1200 ) {

      $fixedHead.css({
        backgroundPosition: '50% -512' + 'px'
      });
    }

    $(window).scroll(function() {

      var wScroll = $(this).scrollTop();
      var headScroll = (-wScroll / 2);
      var faderScroll = (wScroll / 400);
      var fadeToColor = Math.min(faderScroll, 1);

      $shadower.css({
        opacity: fadeToColor
      });

      if (x >= 992 && x <= 1919 ) {

        $fixedHead.css({
          backgroundPosition: '50%' + (-215 + headScroll) + 'px'
        });
      } else if (x >= 1920 && y <= 1199 ) {

        $fixedHead.css({
          backgroundPosition: '50%' + (-430 + headScroll) + 'px'
        });
      } else if (x >= 1920 && y >= 1200 ) {

        $fixedHead.css({
          backgroundPosition: '50%' + (-512 + headScroll) + 'px'
        });
      }

      if (wScroll >= stickyHeight) {
        $falseHeader.addClass('clipped');
      } else {
        $falseHeader.removeClass('clipped');
      }

    });
  }

  function stickySection() {
    var $stickyBar = $('.stickyBar:visible').first();
    if (!$stickyBar.length) return;

    var stickyOffset = $stickyBar.offset().top - 50;

    function updateSticky() {
      if ($(window).scrollTop() > stickyOffset) {
        $stickyBar.addClass('stickyIsFixed');
      } else {
        $stickyBar.removeClass('stickyIsFixed');
      }
    }

    $(window).on('scroll resize', updateSticky);
    updateSticky();
  }

  function smoothScrolling() {
    $('.stickyBar a[href^="#"]').on('click', function(e) {
      e.preventDefault();
      const target = $($(this).attr('href'));
      if (!target.length) return;

      $('.stickyBar .nav-link').removeClass('active');
      $(this).addClass('active');

      $('html, body').animate({
        scrollTop: target.offset().top - 120
      }, 600);
    });
  }

  function activeLinkSwitch() {
  }

  function modalContent() {

    $('a[data-toggle="modal"]').click(function() {
        var dataTarget = $(this).attr('data-target');
        var dataTargetName = $(this).attr('data-target-name');

        $(dataTarget).on('show.bs.modal', function(event) {
          $(this).find('.modal-body').load('https://aikidomusubi.com/photos/' + dataTargetName + '.html');
        });
    });
  }

  function fullCalendarChangeIcons() {

    var svgIconTh = '<svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="th" class="svg-inline--fa fa-th fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M149.333 56v80c0 13.255-10.745 24-24 24H24c-13.255 0-24-10.745-24-24V56c0-13.255 10.745-24 24-24h101.333c13.255 0 24 10.745 24 24zm181.334 240v-80c0-13.255-10.745-24-24-24H205.333c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24h101.333c13.256 0 24.001-10.745 24.001-24zm32-240v80c0 13.255 10.745 24 24 24H488c13.255 0 24-10.745 24-24V56c0-13.255-10.745-24-24-24H386.667c-13.255 0-24 10.745-24 24zm-32 80V56c0-13.255-10.745-24-24-24H205.333c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24h101.333c13.256 0 24.001-10.745 24.001-24zm-205.334 56H24c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24h101.333c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24zM0 376v80c0 13.255 10.745 24 24 24h101.333c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H24c-13.255 0-24 10.745-24 24zm386.667-56H488c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H386.667c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24zm0 160H488c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H386.667c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24zM181.333 376v80c0 13.255 10.745 24 24 24h101.333c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H205.333c-13.255 0-24 10.745-24 24z"></path></svg>';
    var svgIconBars = '<svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="bars" class="svg-inline--fa fa-bars fa-w-14" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="currentColor" d="M16 132h416c8.837 0 16-7.163 16-16V76c0-8.837-7.163-16-16-16H16C7.163 60 0 67.163 0 76v40c0 8.837 7.163 16 16 16zm0 160h416c8.837 0 16-7.163 16-16v-40c0-8.837-7.163-16-16-16H16c-8.837 0-16 7.163-16 16v40c0 8.837 7.163 16 16 16zm0 160h416c8.837 0 16-7.163 16-16v-40c0-8.837-7.163-16-16-16H16c-8.837 0-16 7.163-16 16v40c0 8.837 7.163 16 16 16z"></path></svg>';

    $('.fc-myCustomListWeekButton-button.btn.btn-primary').html(svgIconBars);
    $('.fc-myCustomDayGridWeekButton-button.btn.btn-primary').html(svgIconTh);
  }

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

jQuery(document).ready(function($) {

  hiddenCode();
  revealContent();

  if (document.body.classList.contains('index-8oGCaMDs')) {
    parallaxHeader();
    smoothScrolling();
  }

  if (document.body.classList.contains('training-schedule-IFMn5oCc')) {
    fullCalendarChangeIcons();
  }

  if (document.body.classList.contains('photos-QDOJ1pyG')) {
    modalContent();
  }

  if (document.body.classList.contains('index-8oGCaMDs') || document.body.classList.contains('classes-CJc2lhFv') || document.body.classList.contains('materials-uStNjtHz') || document.body.classList.contains('access-information-NdxqmVbV')) {
    activeLinkSwitch();
    stickySection();
    smoothScrolling();
  }

  console.log('↑ ↑ ↓ ↓ ← → ← → b a');
});

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
