# extractor.rb
require 'anystyle/parser'


f = File.open(ARGV[0], "r")
f.each_line do |line|
  extracted = Anystyle.parse(line, :citeproc)
  result = JSON.generate(extracted[0])
  puts result
end
f.close

# ad = Anystyle.parse('Poe, Edgar A. Essays and Reviews. New York: Library of America, 1984.')
# puts ad.author