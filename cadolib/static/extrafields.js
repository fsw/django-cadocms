if (jQuery != undefined) {
    var django = {
        'jQuery':jQuery,
    }
}
(function($){
    $(document).ready(function($) {
    	
    	function saveExtra(extraDiv){
			var extra = {};
			extraDiv.find("[name^=extra]").each(function(i, elem){
				if($(elem).attr('name') != 'extra')
				{
					var ekey = $(elem).attr('name').substring(6, $(elem).attr('name').length-1);
					if ($(elem).is(':checkbox'))
					{
						extra[ekey] = $(elem).attr('checked') == 'checked';
					}
					else
					{
						extra[ekey] = $(elem).val();
					}
				}
			});
			extraDiv.parent().find('textarea').first().val(JSON.stringify(extra));
		}
		
		function loadExtra(extraDiv){
			var extra = JSON.parse(extraDiv.parent().find('textarea').first().val());
			console.log(extra);
			for (key in extra)
			{
				console.log(extra[key])
				var elem = extraDiv.find("[name=extra\\[" + key + "\\]]");
				if (elem.is(':checkbox'))
				{
					elem.attr('checked', extra[key] ? 'checked' : false);
				}
				else
				{
					elem.val(extra[key]);
				}
			}
		}
		
    	document.registerExtraField = function(url, field_name, provider_name)
    	{
    		///cado/extrafields/unravelling.Item/4
    		field = $('#id_' + field_name);
			var extraDiv = $('<div class="extraFieldsDiv"></div>');
			//field.parents('.form-row').parent().children().first().hide();
			field.after(extraDiv);
			field.hide();
			
    		provider = $('#id_' + provider_name);

			provider.change(function(){
				$.get(url.replace('0', $(this).val()), {}, function(data){
					extraDiv.html(data);
					extraDiv.find("[name^=extra]").change(function(){
						saveExtra(extraDiv);
					});
					loadExtra(extraDiv);
				}, 'html');
			});
			
			provider.change();
    	}
    });
})(django.jQuery);