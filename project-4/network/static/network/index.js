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

async function like(post_id) {
   var heart = document.getElementById(`like-button-${post_id}`)
    if (heart.classList.contains("bi-heart")) {
    heart.classList.toggle("bi-heart");
    heart.classList.toggle("bi-heart-fill");
    } else {
    heart.classList.toggle("bi-heart-fill");
    heart.classList.toggle("bi-heart");
    };

    const response = await fetch(`/post/${post_id}/like`, {
        method: 'PUT',
        headers: { "X-CSRFToken": getCookie('csrftoken') }
    });
    const likes = await response.json();
    heart.innerHTML = ` ${likes.likes}`;
}

async function follow(username) {
    var follow_button = document.getElementById('follow')
    var followers_count = document.getElementById('followers_count')


    if (follow_button.classList.contains("btn-outline-info")) {
        follow_button.classList.toggle("btn-outline-info");
        follow_button.classList.toggle("btn-outline-warning");
        follow_button.innerHTML = "Unfollow";
    } else {
        follow_button.classList.toggle("btn-outline-warning");
        follow_button.classList.toggle("btn-outline-info");
        follow_button.innerHTML = "Follow";
    }

    console.log(follow_button.innerHTML);

    const response = await fetch(`/profile/${username}/follow`, {
        method: 'PUT',
        headers: { "X-CSRFToken": getCookie('csrftoken') }
    });
    const json = await response.json();
    followers_count.innerHTML = `${json.followers}`;
}