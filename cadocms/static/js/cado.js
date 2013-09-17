
jQuery.fn.fixSelectStyles = function() {
	alert(Modernizr.testProp('pointerEvents'));
	alert(this);
};

$(function(){
	if ($('.navbar-fixed-top').length) {
		$('body').css('paddingTop', $('.navbar-fixed-top').height());
		$('.navbar-fixed-top').find('.close').click(function(){
			$(this).parents('.alert').hide();
			$('body').css('paddingTop', $('.navbar-fixed-top').height());
			return false;
		});
	}
});