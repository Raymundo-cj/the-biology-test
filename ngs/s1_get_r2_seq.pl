#!/usr/bin/perl -w
use strict;
open F, $ARGV[0] or die;
open R1,"zcat $ARGV[1]|" or die;
my %hash;

while(<F>){
	my @ss = split;
	for (my $i = 1;$i < @ss;$i++){
		$hash{$ss[$i]} = $ss[0];
	}
}

while(<R1>){
	chomp;
	my @ss=split/\s/,$_;
	my $header=$ss[0];
	chomp(my $sequence=<R1>);
   	chomp(my $comment=<R1>);
    	chomp(my $quality=<R1>);
	if (exists $hash{$header}){
		open NEW, ">>./all_library/$hash{$header}_R2.fastq";
		print NEW "$_\n$sequence\n$comment\n$quality\n";
	}
}
