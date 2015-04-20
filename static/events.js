// Copyright 2009 FriendFeed
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.

var maxEvents=200;

function log(m) {
        //d = document.getElementById("WSLog");
        //d.innerHTML = m + "<br/>" + d.innerHTML;
        console.log(m) ;
      }


function start(websocketServerLocation){
	ws = new WebSocket(websocketServerLocation);
	ws.onopen=function(evt) { log("socket opened"); };
    ws.onmessage = function(evt) { log("event: " + evt.data); };
    ws.onclose = function(){
		log("socket closed");
        //try to reconnect in 5 seconds
        setTimeout(function(){start(websocketServerLocation)}, 5000);
    };
   }


$(document).ready(function() {
	
	$('#domainFilters').multiselect({
		 numberDisplayed: 2,
		 buttonWidth: '200px',
		  includeSelectAllOption: true,
		   enableCaseInsensitiveFiltering: true,
      filterBehavior: 'both',
		buttonClass: 'btn-primary btn-sm',
		nonSelectedText: 'Domain filters',
		maxHeight: 300
		});
		$('#domainFilters').multiselect('dataprovider',domains);
    /*if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#messageform").live("submit", function() {
        newMessage($(this));
        return false;
    });
    $("#messageform").live("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });
    $("#message").select();*/
    
    $('#statusFilters').multiselect({
		 numberDisplayed: 2,
		 buttonWidth: '100px',
		 includeSelectAllOption: true,
		 enableCaseInsensitiveFiltering: true,
         filterBehavior: 'both',
		 buttonClass: 'btn-primary btn-sm',
		 nonSelectedText: 'Status filters',
		 maxHeight: 300
		});
    
    
    
    updater.start();
    log("started");
    console.log("started");
    //streaming
  //  start("ws://localhost:8888/events");
//    var ws = new WebSocket("ws://localhost:8888/events");
//    ws.onopen = function(evt) { log("socket opened"); };
//    ws.onmessage = function(evt) { log("event: " + evt.data); };
//    ws.onclose = function(evt) { log("socket closed"); };
//    ws.onclose = function(evt) { log("socket closed"); setTimeout(function(){ws = new WebSocket("ws://localhost:8888/events")}, 5000); };
	
	
	$('#MarcaTodosDom').change(function() {
		console.log('change function');
		if ($(this).is(":checked")) {
			//alert('check');
			$("#dominiosSelector :input:not(#MarcaTodosDom)").prop("checked", true);
			$('.domainCB').each(function(i){
				dom=deleteSpaces($(this).next('label').text());
				showEventsDomain(dom);
				});
		} else {
			//alert('UNcheck');
			$("#dominiosSelector :input:not(#MarcaTodosDom)").attr("checked", false);
			$('.domainCB').each(function(i){
				dom=deleteSpaces($(this).next('label').text());
				hideEventsDomain(dom);
				});
		}	
	});
	
	$('#MarcaTodosStat').change(function() {
		console.log('change function');
		if ($(this).is(":checked")) {
			//alert('check');
			$("#statusSelector :input:not(#MarcaTodosStat)").prop("checked", true);
			$('.statusCB').each(function(i){
				status=deleteSpaces($(this).next('label').text());
				showEventsStatus(status);
				});
		} else {
			//alert('UNcheck');
			$("#statusSelector :input:not(#MarcaTodosStat)").attr("checked", false);
			$('.statusCB').each(function(i){
				status=deleteSpaces($(this).next('label').text());
				hideEventsStatus(status);
				});
		}	
	});
	
	$('.domainCB').change(function() {
		console.log('change function: '+$(this).next('label').text());
		var dom=deleteSpaces($(this).next('label').text());
		console.log(dom);
		var domname=dom
		var checkedDomains=false
		$('.domainCB').each(function(i){
				d=deleteSpaces($(this).next('label').text());
				if (domname!=d) {
					checkedDomains=$(this).is(":checked")
				//	console.log('dom: '+d+' checked: '+ checkedDomains);
				}
				});
		
		if (checkedDomains) {
			if (!$(this).is(":checked")) {
				$("#dominiosSelector :input:not(#MarcaTodosDom)").attr("checked", false);
				$(this).prop("checked", true);
				$('#MarcaTodosDom').attr("checked", false);
				$('.domainCB').each(function(i){
				d=deleteSpaces($(this).next('label').text());
				hideEventsDomain(d);
				});
				console.log(dom+' domains checked '+$(this).is(":checked"));
				showEventsDomain(dom);
				
			}
		}
		if ($(this).is(":checked")) {
			showEventsDomain(dom);
		} else {
			hideEventsDomain(dom);
		}
	});

	//status
	$('.statusCB').change(function() {
		console.log('change function: '+$(this).next('label').text());
		var stat=deleteSpaces($(this).next('label').text());
		console.log(stat);
		var status=stat
		var checkedStatus=false
		$('.statusCB').each(function(i){
				s=deleteSpaces($(this).next('label').text());
				if (status!=s) {
					checkedStatus=$(this).is(":checked");
				//	console.log('dom: '+d+' checked: '+ checkedDomains);
				}
				});
		
		if (checkedStatus) {
			if (!$(this).is(":checked")) {
				$("#statusSelector :input:not(#MarcaTodosStat)").attr("checked", false);
				$(this).prop("checked", true);
				$('#MarcaTodosStat').attr("checked", false);
				$('.statusCB').each(function(i){
				s=deleteSpaces($(this).next('label').text());
				hideEventsStatus(s);
				});
				console.log(status+' domains checked '+$(this).is(":checked"));
				showEventsStatus(status);
				
			}
		}
		if ($(this).is(":checked")) {
			showEventsStatus(stat);
		} else {
			hideEventsStatus(stat);
		}
	});
	
	
	$('#filterImput').keyup(function () {
		$.expr[":"].contains = $.expr.createPseudo(function(arg) {
			return function( elem ) {
				return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
				};
			});
		var data = this.value.split(" ");
		var rows = $('#eventTableBody').find("tr");
		if (this.value == "") {
			rows.show();
			return;
		} 
		
		rows.hide();
		
		rows.filter(function (i, v) {
			var $t = $(this);
			text=$t.text().toUpperCase();
			//console.log(text);
			 for (var d = 0; d < data.length; ++d) {
				 if ($(this).is(":contains("+data[d]+")")) {
        //    if ($t.is(":contains('" + data[d].toUpperCase() + "')")) {
                return true;
				}
			}
        return false;
		}).show();
		
	}).focus(function() {
		this.value = "";
		 $(this).css({
			"color": "black"
		});
		$(this).unbind('focus');
	}).css({
		"color": "#C0C0C0"
	});
	
	$('#filterLink').bind('click', function () {
		$('.subnav').toggle();
		});
	
	var myData = [
    { label: "Todos", isChecked: false }
  ];

/*$(".myDropdownCheckbox").dropdownCheckbox({
  data: domains,
  autosearch: true,
    title: "My Dropdown Checkbox",
    hideHeader: false,
    showNbSelected: true,
  title: "Dropdown Checkbox",
  templateButton: '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Filters <b class="caret"></b></a>',
});*/


//console.log("items checked: "+$(".myDropdownCheckbox").dropdownCheckbox("checked"));
//console.log("items unchecked: "+$(".myDropdownCheckbox").dropdownCheckbox("unchecked"));

/*$(".myDropdownCheckbox").change(function() {
	
		var allDomains=[];
		var uncheckedDomains=$(".myDropdownCheckbox").dropdownCheckbox("unchecked");
		//var allDomains=domains;
		allDomains=$(".myDropdownCheckbox").data("dropdownCheckbox").data;
		//var checkedDomains=allDomains.checked();
		//console.log(allDomains);
		//console.log(allDomains[0]);
		if (allDomains.data[0].id===0) {
			console.log(allDomains.data[0]);
		}
	
		$.each(allDomains, function(index) {
		//	console.log(allDomains);
			var domainjson = JSON.stringify(index);
			console.log($(this).attr('label')+'-'+$(this).attr('isChecked'));
		});
		
		
		for (var i = 0; i < allDomains.length; i++) {
			console.log(allDomains[i]);
			//console.log('label: '+allDomains.data[i].label +' checked: '+allDomains.data[i].isChecked);	
		};
		for (var i = 0; i < checkedDomains.length; i++) {
			console.log(checkedDomains[i].label);
			//console.log('label: '+allDomains.data[i].label +' checked: '+allDomains.data[i].isChecked);	
		};
		
	});*/
	
$('.dropdown-menu').on('click', function(e) {
    if($(this).hasClass('dropdown-menu-form')) {
        e.stopPropagation();
    }
});

$('#domainFilters').change(function() {
	values=$(this).val();
	if (values!=null) {
		for  (var j = 0; j < domains.length; j++) {
			hideEventsDomain(domains[j].value);
			//console.log(domains[j].value);
		}
		for (var i = 0; i < values.length; i++) {
			showEventsDomain(values[i]);
			//console.log(values[i]);
		}	
	} else {
		for  (var j = 0; j < domains.length; j++) {
			showEventsDomain(domains[j].value);
			//console.log(domains[j].value);
		}
	}
});

var status=[];
status.push({value: 'Open'});
status.push({value: 'ACK'});
status.push({value: 'Closed'});



$('#statusFilters').change(function() {

	values=$(this).val();
	
	if (values!=null) {
		console.log(values);
	//	console.log(status.length);
		for  (var j = 0; j < status.length; j++) {
			hideEventsStatus(status[j].value);
			console.log(status[j].value);
		}
		for (var i = 0; i < values.length; i++) {
			showEventsStatus(values[i]);
			console.log(values[i]);
		}	
	} else {
		for  (var j = 0; j < status.length; j++) {
			showEventsStatus(status[j].value);
			//console.log(domains[j].value);
		}
	}
});


$('#menuoptions li a').click(function(e) {
	console.log('click menu a');
  var $this = $(this);
  
  $('#menuoptions li a').each(function(i) {
	  $(this).parent().removeClass('active');
  });
  $this.parent().addClass('active');
  /*if (!$this.parent().hasClass('active')) {
    $this.parent().addClass('active');
  }
  e.preventDefault();*/
});


$('#maxEvents button').click(function(e) {
	max=maxEvents;
	maxEvents=Number($(this).text());
	console.log(maxEvents);
	if (maxEvents<max) {
		console.log('clearing: '+max+'max'+maxEvents);
		clearEvents(maxEvents);
	}
});



	
$("#fulllogLinkAjax").click(function(){
	var message = {body: "fulllog"}
    $.postJSON("/a/fulllog", message, function(response) {
		//console.log('respuesta'+response);
		$(".tableDiv").empty();
		$(".tableDiv").append(response);
		
	});    
}); 

$("#realtimeLinkAjax").click(function(){
	var message = {body: "realtimelog"}
    $.postJSON("/a/realtime", message, function(response) {
		//console.log('respuesta'+response);
		$(".tableDiv").empty();
		$(".tableDiv").append(response);
		
	});    
}); 

	
}); //documentReady

//AJAX
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
	console.log(args._xsrf );
    $.ajax({
		url: url, 
		data: $.param(args), 
		dataType: "text",
		type: "POST", 
        success: function(response) {
			//console.log('success');
			//console.log(response);
			//callback(eval("(" + response + ")"));
			callback(response);
			console.log('success');
		},
		beforeSend: function () {
			//$("#test").html("Procesando, espere por favor...");
			$(".tableDiv").html("<div class='text-center'><img id='loading' src='/static/ajax-loader.gif' alt='loading...' /></div>");
			//var parent_height = $('#loading').parent().height();
			//var image_height = $('#loading').height();
			//var top_margin = (parent_height - image_height)/2;
			//$('#loading').css( 'margin-top' , top_margin);
			console.log('Procesando...');
        },
    });
};

//AJAX


$("#btnlogout").click(function(){
        window.location.href='/auth/logout/';
    }); 
	
$("#btnclr").click(function(){
	console.log('clear');
        $(".tableDiv").empty();
    }); 

//Domains
function showEventsDomain(d) {
	ev = $('.domaintd');
	//console.log("show domain "+d);
	ev.each(function(i) {
		//console.log($(this).text());
		if (deleteSpaces($(this).text())===d) {
			$(this).parent().show();
		}
	});	
}


function hideEventsDomain(d) {
	//console.log("hide domain "+d);
	ev = $('.domaintd');
	ev.each(function(i) {
		//console.log($(this).text());
		if (deleteSpaces($(this).text())===d) {
			$(this).parent().hide();
		}
	});	
}

//Status
function showEventsStatus(s) {
	ev = $('.statustd');
	//console.log("show domain "+d);
	ev.each(function(i) {
		//console.log($(this).text());
		if (deleteSpaces($(this).text())===s) {
			$(this).parent().show();
		}
	});	
}


function hideEventsStatus(s) {
	//console.log("hide domain "+d);
	ev = $('.statustd');
	ev.each(function(i) {
		//console.log($(this).text());
		if (deleteSpaces($(this).text())===s) {
			$(this).parent().hide();
		}
	});	
}

function newMessage(form) {
    var message = form.formToDict();
    updater.socket.send(JSON.stringify(message));
    form.find("input[type=text]").val("").select();
}

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};


var updater = {
    socket: null,

    start: function() {
		uri = location.pathname;
		switch(uri) {
			case '/full':
				var url = "ws://" + location.host + "/events?full";
				break;
			default:
				var url = "ws://" + location.host + "/events";
		}//switch
        
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
        updater.socket.onclose = function(){
        //try to reconnect in 5 seconds
        $('#userlogTable').html('<tr class="danger"><td>DISCONNECTED</td></tr>');
        setTimeout(function(){updater.start()}, 5000);
		};
	},

    showMessage: function(message) {
        var existing = $("#m" + message.id);
        
        switch(message.option) {
			case 'update':
				//console.log('update');
				updateEvent(message);
				break;
			case 'users':
				//console.log('users');
				updateUsers(message);
				break;
			default:
				//console.log('default');
				eventlog('<tr class="warning"><td>Option: '+message.option+' ID: '+message.id+'</td></tr>');
				if (existing.length > 0) return;
				var node = $(message.html);
				node.hide();
				$("#eventTableBody").prepend(node);
				clearEvents(maxEvents);
				//console.log(message.domain);
				domain=deleteSpaces(message.domain);
				filterDom=$('#domainFilters').val();
				if ( filterDom!=null ) {
					if ( isactive(domain, filterDom) ) {
						$('#tr'+ message.id).show();
					} else {
						$('#tr'+ message.id).hide();
					}
				} else {
					$('#tr'+ message.id).show();
				}	
			}//switch
    }
};


function updateEvent(m) {
	$("#s"+m.id).html('<small>'+m.status+'</small>').css('font-weight', 'bold');
	$("#u"+m.id).html('<small>'+m.user+'</small>').css('font-weight', 'bold');
	eventlog('<tr class="danger"><td>Event '+m.id+' updated to '+m.status+' by user '+m.user+'</td></tr>');	 
}

function updateUsers(m) {
	$('#userlogTable').html('<tr class="success"><td>'+m.body+'</td></tr>');
	if (m.action=='Connected') {
		eventlog('<tr class="info"><td>User logged from '+m.remote_ip+'</td></tr>');
	} else {
		eventlog('<tr class="danger"><td>User disconnected '+m.remote_ip+'</td></tr>');
	}
}

/*function controlLogTable() {
	var maxRows = 10;  //added 1 to not count header
	var rowCount = $("#logTable tr").length;
	console.log('rows: '+rowCount);
	while (rowCount >= maxRows+1) {
		$("#logTable tr:last").remove();
		rowCount = $("#logTable tr").length;
		console.log('lastRow deleted');
	}
}*/

function isactive(d,l) {
	//check if d is in list l
	var has = false;
	for (var i=0; i<l.length; i++) {
		if (d===l[i]) {
			has = true;
		}
	}
	return has;
}

function eventlog(m) {
	$("#logTable").prepend(m);
	
	var maxRows = 20;  //added 1 to not count header
	var rowCount = $("#logTable tr").length;
	//console.log('rows: '+rowCount);
	while (rowCount >= maxRows+1) {
		$("#logTable tr:last").remove();
		rowCount = $("#logTable tr").length;
		//console.log('lastRow deleted');
	}
}

function clearEvents(m) {
	var maxRows = m;  //added 1 to not count header
	var rowCount = $("#eventTableBody tr").length;
	//console.log(rowCount);
	//console.log('rows: '+rowCount);
	ev = $('.statustd');
	//console.log(ev);
	ev = $(".statustd").get().reverse();
	//console.log(ev);
	$(ev).each(function() {
		//console.log($(this).text());
		if (rowCount >= maxRows+1) {	
			if (deleteSpaces($(this).text())==="Closed") {
				$(this).parent().remove();
			//	console.log('lastRow deleted');
			}
		}
		rowCount = $("#eventTableBody tr").length;
	});	
	
	while (rowCount >= maxRows+1) {
		$("#eventTableBody tr:last").remove();
		rowCount = $("#eventTableBody tr").length;
	}
		//$("#eventTableBody tr:last").remove();
}

function deleteSpaces(s) {
	console.log(s);
	words=s.split(" ");
	ns='';
	for (var d = 0; d < words.length; ++d) {
		ns=ns+words[d];
	}
	return ns
}

