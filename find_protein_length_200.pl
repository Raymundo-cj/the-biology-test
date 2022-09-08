#!usr/bin/perl
use warnings;
use strict;

my ($file,$output)=@ARGV;

open FILE,"$file";
open OUTPUT,">$output";

my ($seq_order,$seq_name,%hash_fasta,$length,%count,@array);

while(<FILE>){
        chomp;
        if(/^>/){
                @array=split/\s+/;
                $seq_order++;
                $seq_name = $array[0];
        }
        else{
                $hash_fasta{$seq_name} .= $_;
        }
}

#foreach (keys %hash_fasta){
#       $count{$hash_fasta{$_}}++;}


foreach (keys %hash_fasta){
#       $length =length($hash_fasta{$_});
        my $fa=$hash_fasta{$_};my @coun=split(/\*/,$fa);
        $length =length($coun[0]);
        if ($length >=200 and $fa=~/\*/g){
#               my @coun=split(/\*/,$fa);
