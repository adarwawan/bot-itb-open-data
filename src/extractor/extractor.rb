# extractor.rb
require 'anystyle/parser'


f = File.open(ARGV[0], "r")
f.each_line do |line|
  result = Anystyle.parse(line, :citeproc).to_s  
  puts result
end
f.close

# ad = Anystyle.parse('Poe, Edgar A. Essays and Reviews. New York: Library of America, 1984.')
# puts ad.author