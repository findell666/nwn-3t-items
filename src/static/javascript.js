function selectAll(elt){
    $(elt).parent().find("[type=checkbox]").prop("checked", true).trigger("change");
}
function unselectAll(elt){
    $(elt).parent().find("[type=checkbox]").prop("checked", false).trigger("change");;
}

function toggleAllBaseItemsCategory(elt){
    if(!$(elt).prop("checked")){
        unselectAll(elt);
    }
    else{
        selectAll(elt)
    }
}

function removeFile(elt){
    var fileName = $(elt).attr("file-name");
    var attachments = $("#pcfiles")[0].files;
    var fileBuffer = new DataTransfer();

    for (var i = 0; i < attachments.length; i++) {
        if (fileName !== attachments[i].name){
            fileBuffer.items.add(attachments[i]);
        }
    }
    $("#pcfiles")[0].files = fileBuffer.files;
}

$(function(){

    $('input[type=file]').change(function (e) {
        $('.element-to-paste-filename').empty();
        for(var i = 0; i< e.target.files.length; i++){
            var listItem = $("<li class='list-group-item d-flex justify-content-between align-items-start'></li>");
            listItem.text(e.target.files[i].name);
            var closeButton = $("<i title='Remove from list' file-name='"+e.target.files[i].name+"' class='bi-x'></i></li>");
            closeButton.click(function(){
                removeFile(this);
                $(this).parent().remove();
            });
            listItem.append(closeButton);
            $('.element-to-paste-filename').append(listItem);

        }
    });

  

    //init state
    $("#filterItemsByType").hide();

    $("#toggleFilterItemsByType").click(function(){        
        $("#filterItemsByType").toggle();

        var isVisible = $("#filterItemsByType").is(":visible");
        if(isVisible){
            $(this).text("CLOSE")
        }
        else{
            $(this).text("OPEN")
        }        
    });


    $("#exportToCsv").submit(function(){

        if ($('#pcfiles')[0].files.length === 0) {
            alert("Select at least one .bic file");
            return false;
        }

    })

    $("[type=checkbox]").change(function(){
        console.log("change")
        var id = $(this).attr("id");
        console.log($(this).prop("checked"))
        localStorage.setItem(id, $(this).prop("checked").toString()); 
    })

    $("[type=checkbox]").each(function(){
        var id = $(this).attr("id");
        var state = localStorage.getItem(id);
        if(null != state && undefined != state && "" != state){
            console.log(state)
            $(this).prop("checked", state == 'true')
        }
    })    

})