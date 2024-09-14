<!DOCTYPE html>
<html>
<head>
    <title>Login Result</title>
</head>
<body>
    <h1>Login Result</h1>
    
    <?php
$data = array(
    'username' => 'lahiru',
    'password' => '123lahiru',
);
 $_POST = $data;$data = array(
    'username' => 'lahiru',
    'password' => '123lahiru',
);
 $_POST = $data;
 $_POST = $data;    if (isset($_POST['username']) && isset($_POST['password'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];
        
        echo "Username: $username<br>";
        echo "Password: $password";
    } else {
        echo "POST data not received or fields are missing.";
    }
    ?>
</body>
</html>
