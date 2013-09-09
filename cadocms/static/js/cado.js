
jQuery.fn.fixSelectStyles = function() {
	alert(Modernizr.testProp('pointerEvents'));
	alert(this);
};

$(function(){
	if ($('.navbar-fixed-top').length) {
		$('body').css('paddingTop', $('.navbar-fixed-top').height());
	}
});