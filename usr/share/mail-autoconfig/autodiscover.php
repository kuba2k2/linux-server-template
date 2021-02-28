<?php
$data = file_get_contents("php://input");
preg_match("/\<EMailAddress\>(.*?)\<\/EMailAddress\>/", $data, $matches);
$email = $matches[1];
if (!$email) {
	header('HTTP/1.1 500 Internal Server Error');
	exit;
}
$domain = substr($email, strpos($email, '@') + 1);
$domain = explode('.', $domain);
$domain = array_reverse($domain);
$domain = $domain[1].'.'.$domain[0];
header("Content-Type: application/xml");
?>
<?xml version="1.0" encoding="utf-8" ?>
    <Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
        <Response xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
        <Account>
            <AccountType>email</AccountType>
            <Action>settings</Action>
            <Protocol>
                <Type>POP3</Type>
		<Server>pop3.<?=$domain ?></Server>
                <Port>995</Port>
		<LoginName><?=$email ?></LoginName>
                <DomainRequired>off</DomainRequired>
                <SPA>off</SPA>
                <SSL>on</SSL>
                <AuthRequired>on</AuthRequired>
            </Protocol>
            <Protocol>
                <Type>IMAP</Type>
		<Server>imap.<?=$domain ?></Server>
                <Port>993</Port>
		<LoginName><?=$email ?></LoginName>
                <DomainRequired>off</DomainRequired>
                <SPA>off</SPA>
                <SSL>on</SSL>
                <AuthRequired>on</AuthRequired>
            </Protocol>
            <Protocol>
                <Type>SMTP</Type>
		<Server>smtp.<?=$domain ?></Server>
                <Port>465</Port>
		<LoginName><?=$email ?></LoginName>
                <DomainRequired>off</DomainRequired>
                <SPA>off</SPA>
                <SSL>on</SSL>
                <AuthRequired>on</AuthRequired>
            </Protocol>
        </Account>
    </Response>
</Autodiscover>
