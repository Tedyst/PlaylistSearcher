<html>

<head>
    <title>Search</title>
</head>

<body>
Found the word <b>{{text}}</b> in:
% for i in results:
    <br>
    {{i.name}} - {{i.main_artist}}
% end
</body>

</html>