$(function(){
  $("select#cmap_data_family").change(function(){
    $.getJSON("/cgi-bin/mpservice.py?data_family=" + $("select#cmap_data_family").val(),{id: $(this).val(), ajax: 'true'}, function(j){

      var options = '<option value="">Select</option>';
      for (var i = 0; i < j.length; i++) {
        options += '<option value="' + j[i].optionValue + '">' + j[i].optionDisplay + '</option>';
      }
      $("select#cmap_data_category").html(options);
   return false; 
   })
})

  $("select#cmap_data_category").change(function(){
    $.getJSON("/cgi-bin/mpservice.py?data_cat=" + $("select#cmap_data_category").val(),{id: $(this).val(), ajax: 'true'}, function(j){

      var options = '<option value="">Select</option>';
      for (var i = 0; i < j.length; i++) {
        options += '<option value="' + j[i].optionValue + '">' + j[i].optionDisplay + '</option>';
      }
      $("select#cmap_data_subcategory").html(options);

   return false;
   })
  })

  $("select#cmap_data_subcategory").change(function(){
    $.getJSON("/cgi-bin/mpservice.py?data_subcat=" + $("select#cmap_data_subcategory").val(),{id: $(this).val(), ajax: 'true'}, function(j){

      var options = '<option value="">Select</option>';
      for (var i = 0; i < j.length; i++) {
        options += '<option value="' + j[i].optionValue + '">' + j[i].optionDisplay + '</option>';
      }
      $("select#cmap_data_field").html(options);

   return false;
   })
  })

})
