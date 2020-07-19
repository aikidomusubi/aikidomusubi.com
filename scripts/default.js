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

  function smoothScrolling() {

    $('#index-8oGCaMDs-nav a[href*=\\#]:not([href=\\#])').click(function() {
      if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
        var target = $(this.hash);
        target = target.length ? target : $('[id=' + this.hash.slice(1) +']');
        if (target.length) {
          $('html,body').animate({
            scrollTop: target.offset().top - 126
          }, 1000);
          return false;
        }
      }
    });
  }

  function modalContent() {

    $('a[data-toggle="modal"]').click(function() {
        var dataTarget = $(this).attr('data-target');
        var dataTargetName = $(this).attr('data-target-name');

        $(dataTarget).on('show.bs.modal', function(event) {
          $(this).find('.modal-body').load('http://localhost:4000/photos/' + dataTargetName + '.html');
        });
    });

    // $('.modal').on('show.bs.modal', function(event) {
    //   $(this).find('.modal-body').load('');
    // });
  }

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

jQuery(document).ready(function($) {

  hiddenCode();
  revealContent();
  smoothScrolling();
  modalContent();

  if (document.body.classList.contains('index-8oGCaMDs')) {
    parallaxHeader();
  }

  console.log('↑ ↑ ↓ ↓ ← → ← → b a');
});

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
