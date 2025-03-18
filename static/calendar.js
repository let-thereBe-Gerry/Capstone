function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      } 
  }
  return cookieValue;
}

// pag nasa outside yung code, pag binabago ayaw lumabas.  
document.addEventListener('DOMContentLoaded', function() {
var csrfToken = "{{ csrf_token }}";
var calendarEl = document.getElementById('calendar');

// Get the current date
var currentDate = new Date();

// Format the date as 'YYYY-MM-DD'
var formattedDate = currentDate.toISOString().slice(0, 10);


var calendar = new FullCalendar.Calendar(calendarEl, {
headerToolbar: {
left: 'prev,next today',
center: 'title',
right: 'dayGridMonth,timeGridWeek,timeGridDay'
},

initialDate: formattedDate,

navLinks: true, // can click day/week names to navigate views
selectable: true,
selectMirror: true,

select: function(arg) {
var title = prompt('Event Title:');
if (title) {
  calendar.addEvent({
      title: title,
      start: arg.start,
      end: arg.end,
      allDay: arg.allDay
  });

  // bakit hindi lumalabas yung calendar? hmmm
  var data_toSend = {
      appt_title: title,
      appt_start: arg.start.toISOString(),
      appt_end: arg.end.toISOString(),
      appt_allDay: arg.allDay,
      csrfmiddlewaretoken: csrfToken
  };
  

  fetch('/save_event/', {
      method: 'POST',  // POST or GET? -- if ginawa ko s'yang GET, walang nag ssave even empty data
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(data_toSend)
  })

  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
}
calendar.unselect();
},

eventClick: function(arg) {
if (confirm('Are you sure you want to delete this event?')) {
arg.event.remove()
}
},
editable: true,
dayMaxEvents: true, // allow "more" link when too many events

events: '/get_events/' + clinicId + '/', 
// all the event should be coming in the database - hindi pa rin nag didisplay huhu -- maybe kaya hindi nag ddisplay kasi empty yung data? 

});
console.log('TEST ONE ~~~~~~~~~~~~~~~~~~~~~~~~~ N1');
console.log('Clinic ID:', clinicId);

calendar.render();
});