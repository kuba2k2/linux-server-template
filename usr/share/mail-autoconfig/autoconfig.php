<?php
$email = $_GET['emailaddress'];
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
<clientConfig version="1.1">
	<emailProvider id="<?=$domain ?>">

		<domain><?=$domain ?></domain>

		<displayName><?=$email ?></displayName>
		<displayShortName><?=$email ?></displayShortName>

		<incomingServer type="pop3">
			<hostname>pop3.<?=$domain ?></hostname>
			<port>995</port>
			<socketType>SSL</socketType>
			<username><?=$email ?></username>
			<authentication>password-cleartext</authentication>
		</incomingServer>

		<incomingServer type="imap">
			<hostname>imap.<?=$domain ?></hostname>
			<port>993</port>
			<socketType>SSL</socketType>
			<username><?=$email ?></username>
			<authentication>password-cleartext</authentication>
		</incomingServer>

		<outgoingServer type="smtp">
			<hostname>smtp.<?=$domain ?></hostname>
			<port>465</port>
			<socketType>SSL</socketType>
			<username><?=$email ?></username>
			<authentication>password-cleartext</authentication>
			<addThisServer>true</addThisServer>
			<useGlobalPreferredServer>true</useGlobalPreferredServer>
		</outgoingServer>

	</emailProvider>
</clientConfig>
