<html>

<head>
    <title>Search</title>
</head>

<body>
<a href="/">Back</a>
<br>
Found the word <b>{{text}}</b> in:
% for i in results:
    <br>
    {{i.name}} - {{i.main_artist}}
% end
</body>

</html>