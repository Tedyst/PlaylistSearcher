<html>

<head>
    <title>Spotify</title>
</head>

<body>
<form action="search" method="GET">
    <select name="playlist">
        % for i in playlists:
        <option value="{{i['id']}}">{{i['name']}}</option>
        % end
    </select>
    <input type="text" name="text" placeholder="Text to search"/>
    <input type="submit" value="Submit the form"/>
</form>
    
</body>

</html>