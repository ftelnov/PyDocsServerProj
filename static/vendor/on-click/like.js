function like(img) {
    const url = '/api/like/set';
    const request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader('Content-Type', 'application/json');
    request.onreadystatechange = function () {
        if (request.readyState == XMLHttpRequest.DONE) {
            const result = JSON.parse(request.responseText);
            if ('Like already placed!' === result['result']) {
                const request_remove = new XMLHttpRequest();
                request_remove.open("POST", '/api/like/remove', true);
                request_remove.setRequestHeader('Content-Type', 'application/json');
                request_remove.send(JSON.stringify({
                    'author': img.name,
                    'peer_id': img.id
                }));
                img.src = "../static/img/non-like.png"
            }
            else if ('Success!' === result['result']) {
                img.src = "../static/img/like.png"
            }
        }
    };

    request.send(JSON.stringify({
        'author': img.name,
        'peer_id': img.id
    }));

}