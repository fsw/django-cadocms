$(function($) {
	
	fakeStack = new Array();
	
	function changeSelect(){
		$(this).nextAll('select').remove();
		real = $(this).prevAll('input'); 
		root = real.next();
		if ($(this).val()){
			real.val($(this).val());
			that = this;
			$.ajax({
				  url: root.attr('data-urlchildren').replace('0', $(this).val()),
				  dataType: "json",
				  success: function(data) {
					  if(! $.isEmptyObject(data)){
						  $next = $('<select></select>');
						  $next.append( '<option value="">-ALL-</option>' );
						  $.each(data, function(id, name) {
							  $next.append( '<option value="' + id + '">' + name + '</option>' ); 
						  });
						  $next.change(changeSelect);
						  $(that).after($next);
						  $next.val(fakeStack.shift());
						  $next.change();
					  }
				  }
			});
		} else {
			if($(this).is(root)) {
				real.val($(this).val());
			} else {
				real.val($(this).prev().val());	
			}
		}
	}
	
	$('.stackedselect').each(function(i,e){
		$(e).before('<input type="hidden" name="' + $(e).attr('name') + '" value="' + $(e).attr('data-value') + '"/>');
		$(e).attr('name', '');
		
		$.ajax({
			  url: $(e).attr('data-urlpath').replace('0', $(e).attr('data-value')),
			  dataType: "json",
			  success: function(data) {
				  fakeStack = data;
				  //console.log(fakeStack);
				  fakeStack.shift();
				  $(e).change(changeSelect);
				  //console.log(fakeStack);
				  $(e).val(fakeStack.shift());
				  $(e).change();
			  }
		});
		
	});
	
});