function like(img) {
    const url = '/api/like/set';
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    console.log(img.name, img.id);
    xhr.onreadystatechange = function () {
        var result = JSON.parse(Http.responseText);
        console.log(1);
        if ('Like already placed!' === result['result']) {
            xhr.open("POST", '/api/like/remove', true);
            xhr.send(JSON.stringify({
                'author': img.name,
                'peer_id': img.id
            }));
            img.src = "../static/img/non-like.png"
        }
        else if ('Success!' === result['result']) {
            img.src = "../static/img/like.png"
        }
    }

    xhr.send(JSON.stringify({
        'author': img.name,
        'peer_id': img.id
    }));

}