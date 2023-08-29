#!/usr/bin/perl -w
use strict;
open R1,"zcat $ARGV[0]|" or die;
open R2,"zcat $ARGV[1]|" or die;

my %hash_barcode1;my %hash;my %hash_pairs;

while(<R1>){
	chomp;
	my @ss=split/\s/,$_;
	my $header=$ss[0];
    	chomp(my $sequence=<R1>);
    	chomp(my $comment=<R1>);
    	chomp(my $quality=<R1>);
	$sequence =~ /GCTT(.+?)TGGAGTGAGTACGGTGTGC/; my $barcode1= $1;
	if (length($barcode1)==4){
		$hash_barcode1{$header} = $barcode1;
	}
}
my $header;my $pairs;
while(<R2>){
	chomp;
	my @ss=split/\s/,$_;
	$header=$ss[0];
    	chomp(my $sequence=<R2>);
    	chomp(my $comment=<R2>);
    	chomp(my $quality=<R2>);
	$sequence =~ /CTGT(.+?)TGAGTTGGATGCTGGATGG/; my $barcode2= $1;
	if (length($barcode2)==4){
		$pairs = $hash_barcode1{$header}."_$barcode2";
		if (exists $hash_pairs{$pairs}){
			$hash_pairs{$pairs} = $hash_pairs{$pairs}."\t$header";
		}else{
			$hash_pairs{$pairs} = $header;
		}
	}
}
foreach my $key (keys %hash_pairs){
	print "$key\t$hash_pairs{$key}\n";
}
