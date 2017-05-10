#!/usr/bin/perl -w
use strict;
use LWP::UserAgent;
use HTTP::Request::Common qw(POST);
use File::Basename;

#$ENV{'PERL_LWP_SSL_VERIFY_HOSTNAME'} = 0;

# BMC Software
# Matthew Salerno
# -
# Bulk Scan File upload
#

# TODO
# SCCM or BSA
# Build scan file list
# Select Severity
# Select Vendor
# change myserver to reflect your actual server

my $loginurl = 'https://myserver.us-east-1.elb.amazonaws.com/dcaportal/api/login';
my $scanuploadurl = 'https://myserver.us-east-1.elb.amazonaws.com/dcaportal/api/vulnerability/importScan';

# Where to get the file, currently hardcoded
my $scanfile = "/Users/msalerno/Downloads/testscan.xml";

# change username and password as needed.  .sccm indicates "sccm" side, .bsa for "BSA"

my $loginstr = 
q|{
  "authenticationMethod":"SRP",
  "username": "myuser@mysite.sccm",
  "password":"password"
}|;

my $ua = LWP::UserAgent->new();
$ua->cookie_jar( {} );

my $clientid = login($ua, $loginurl, $loginstr);

my $uploadstatus = uploadscan($ua, $clientid, $scanuploadurl, $scanfile);
print $uploadstatus;

sub uploadscan {
	my $ua = shift;
	my $clientid = shift;
	my $scanuploadurl = shift;
	my $scanfile = shift;
	my $scanfilename = basename $scanfile;

	my $uploadreq = POST $scanuploadurl,
	[
	$scanfilename => ["$scanfile", undef, "Content-Type" => "text/xml"],
	osTobeConsidered => 'Linux,Windows',
	severitiesTobeConsidered => 'Severity 1,Severity 2,Severity 3,Severity 4,Severity 5',
	selectedVendor => 'Qualys'
	],
	Content_Type => 'form-data';
	
	$uploadreq->header(ClientId => $clientid);

	$ua->prepare_request($uploadreq);
	my $upresponse = $ua->send_request($uploadreq);
	return $upresponse->as_string;
}

sub login {
	my $ua = shift;
	my $loginurl = shift;
	my $loginstr = shift;
	my $req = HTTP::Request->new( POST => $loginurl);
	$req->content_type('application/json');
	$req->content($loginstr);
	my $res = $ua->request($req);

	if ($res->is_success) {
		($clientid) = $res->decoded_content =~ m/.*clientId":"(.*)".*/g;
		return $clientid;
	}
	else {
		die $res->status_line;
	}
}
