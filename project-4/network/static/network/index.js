function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function put_like(post_id) {
   var heart = document.getElementById(`like-button-${post_id}`)
    if ("bi-heart" in heart.classList) {
    heart.classList.toggle("bi-heart");
    heart.classList.toggle("bi-heart-fill");
    } else {
    heart.classList.toggle("bi-heart-fill");
    heart.classList.toggle("bi-heart");
    }

    const response = await fetch(`/post/${post_id}/put_like`, {
        method: 'PUT',
        headers: { "X-CSRFToken": getCookie('csrftoken') }
    });
    const likes = await response.json();
    heart.innerHTML = ` ${likes.likes}`;
}