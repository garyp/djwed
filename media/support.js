

function rsvpHideIfNotAttending(obj) {
    //obj.style.border = "solid 4pt blue";
    //alert(obj);
    //obj.parentNode.style.border = "solid 4pt red";
    curValue = obj.getElementsByTagName("select")[0].value;
    //alert(curValue);
    div_ifattend = obj.parentNode.getElementsByClassName("IfAttending")[0];
    if (curValue == "y" || curValue == "m" || curValue == "v") {
	//div_ifattend.style.border = "solid 4pt green";
	div_ifattend.style.display = "block";
    } else {
	//div_ifattend.style.border = "solid 4pt yellow";
	div_ifattend.style.display = "none";
    }
	
}

function rsvpHideIfNotAttendingSelect(obj) {
    //obj.style.border = "solid 4pt blue";
    //alert(obj);
    //obj.parentNode.style.border = "solid 4pt red";
    curValue = obj.value;
    div_ifattend = obj.parentNode.parentNode.parentNode.getElementsByClassName("IfAttending")[0];
    if (curValue == "y" || curValue == "m" || curValue == "v") {
	//div_ifattend.style.border = "solid 4pt green";
	div_ifattend.style.display = "block";
    } else {
	//div_ifattend.style.border = "solid 4pt yellow";
	div_ifattend.style.display = "none";
    }
	
}

function rsvpHideBasedOnAttending(obj) {
    divs = window.document.getElementsByClassName("AttendingSelect");
    var i;
    for (i=0; i < divs.length; i++) {
	rsvpHideIfNotAttending(divs[i]);
    }    
}
