document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

  // By default, load the inbox
  load_mailbox('inbox');


});

function compose_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';



  if (email === undefined){
      // Clear out composition fields
      document.querySelector('#compose-recipients').value = '';
      document.querySelector('#compose-subject').value = '';
      document.querySelector('#compose-body').value = '';
    } else {
        if (email['subject'].includes("Re: ")){
            document.querySelector('#compose-subject').value = email['subject'];
        } else {
            document.querySelector('#compose-subject').value = `Re: ${email['subject']}`;
        };
        document.querySelector('#compose-body').value = `On ${email['timestamp']} ${email['sender']} wrote:\n${email['body']}`;
        document.querySelector('#compose-recipients').value = email['sender'];
    };

    document.querySelector('form').addEventListener("submit", send_email);
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fatch emails
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {emails.forEach(add_email)});

  function add_email(email_content){

      // Create Item
      const item = document.createElement('div');
      item.className = 'em';

      //Changing background if open
      if (email_content['read'] === true) {
      item.style.background = 'white';
      };

      //Adding contact to email
      const contact = document.createElement('div');
      if (mailbox === 'sent') {
          // Adding sender to contact
          contact.innerHTML = `To: ${email_content['recipients']}`;
      } else {
          // Adding sender to contact
          contact.innerHTML = `From: ${email_content['sender']}`;
      }
      item.append(contact);

      // Adding subject to email
      const subject = document.createElement('div');
      subject.innerHTML = email_content['subject'];
      item.append(subject);

      // Adding timestamp to email
      const timestamp = document.createElement('div');
      timestamp.innerHTML = email_content['timestamp'];
      item.append(timestamp);

      // Archive button
      const button = document.createElement('button');
      if (mailbox === 'inbox'){
          button.innerHTML = 'Archive';
          button.addEventListener('click', () => set_archived(email_content['id'], true));

          item.append(button);
      } else if (mailbox == 'archive'){
          button.innerHTML = 'Unarchive';
          button.addEventListener('click', () => set_archived(email_content['id'], false));
          item.append(button);
      }

      // Open email
      item.addEventListener('click', () => get_email(email_content['id']));

      // Add email to DOM
      document.querySelector('#emails-view').append(item);

  }
}


function send_email() {
  const form = document.querySelector('form');
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: form.elements['compose-recipients'].value,
      subject: form.elements['compose-subject'].value,
      body: form.elements['compose-body'].value
    })
  });
  load_mailbox('sent');
  return false
}

  function get_email(id){
      // Show the email and hide other views
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#email-view').style.display = 'block';
      document.querySelector('#compose-view').style.display = 'none';

      // Clear previous data
      document.querySelector('#email-view').innerHTML = '';

      // Get email details
      fetch(`/emails/${id}`)
        .then(response => response.json())
        .then(email => {

            if (email['read'] === false){
                put_read(id)
            }

            // Shown details
            const email_detail = document.createElement('div');

            // Adding sender
            const from = document.createElement('div');
            from.innerHTML = `From: ${email['sender']}`;
            email_detail.append(from);

            // Adding recipients
            const to = document.createElement('div');
            to.innerHTML = `To: ${email['recipients']}`;
            email_detail.append(to);

            // Adding subject to email
            const subject = document.createElement('div');
            subject.innerHTML = `Subject: ${email['subject']}`;
            email_detail.append(subject);

            // Adding subject to email
            const body = document.createElement('div');
            body.innerHTML = `Body: ${email['body']}`;
            email_detail.append(body);

            const reply = document.createElement('button');
            reply.innerHTML = `Reply`;
            reply.addEventListener("click", () => compose_email(email));
            email_detail.append(reply);

            document.querySelector('#email-view').append(email_detail);
            });
  }



function set_archived(id, state){

    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
          archived: state
      })
    })
    document.location.reload(true)
}

function put_read(id){
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
          read: true
      })
    })
}