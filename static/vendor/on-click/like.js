function like(img, peer_id, login) {
    var body = 'peer_id=' + encodeURIComponent(peer_id) +
        '&login=' + encodeURIComponent(login);
    const Http = new XMLHttpRequest();
    const url = '/api/like/set';
    Http.open("POST", url, true);
    Http.send(body);
    Http.onreadystatechange = (e) => {
        var result = JSON.parse(Http.responseText);
        if ('Like already placed!' === result['result']) {
            Http.open("POST", '/api/like/remove', true);
            var body_two = 'peer_id=' + encodeURIComponent(peer_id) +
                '&login=' + encodeURIComponent(login) + '&password=' + encodeURIComponent(password);
            Http.send(body);
            img.src = "../static/img/non-like.png"
        }
        else if('Success!' === result['result']){
            img.src = "../static/img/like.png"
        }
    }
}