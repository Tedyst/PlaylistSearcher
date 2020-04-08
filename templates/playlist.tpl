<html>

<head>
    <title>Search</title>
</head>

<body>
<a href="/">Back</a>
Search made in <b>{{elapsed}}</b> seconds
<br>
Found the word <b>{{text}}</b> in:
% for i in results:
    <br>
    {{i.name}} - {{i.main_artist}}
% end
</body>

</html>