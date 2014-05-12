#This script searches the foreman API for an envtag and a client, then outputs the hosts in JSON format for Rundeck to consume.

require 'json'
require 'jsonpath'
require 'pp'
require 'uri'
require 'open-uri'
require 'net/https'
require 'enumerator'
searchstr=URI.encode('search=name=cnx_envtag||name=cnx_client')
# disable ssl verification, be careful!
module OpenSSL
  module SSL
    remove_const :VERIFY_PEER
  end
end
OpenSSL::SSL::VERIFY_PEER = OpenSSL::SSL::VERIFY_NONE




#create an array of hostnames
hosts = JSON.parse(open("https://foreman.ct.com/api/v2/fact_values?search=name=hostname", :http_basic_authentication=>["user","pass"]).read)
#parse the output of our search url to json
json_object = JSON.parse(open("https://foreman.ct.com/api/v2/fact_values?#{searchstr}", :http_basic_authentication=>["user","pass"]).read)
#get the hostnames from our 'hosts' search
path = JsonPath.new('$..hostname')
@hostlist = path.on(hosts)
#append .cloud.connecture.com so the hostnames match.  Probably could've done this with a different fact, like fqdn, but I didn't come here to be judged by so.
@hostlist.map! { |e| e + ".cloud.connecture.com" }
#Only keep hosts that show up in our search results
 	@hostlist.keep_if {|name| json_object["results"].has_key?("#{name}")}
#Now we need to drop everything that doesn't have an envtag, could use @hostlist.keep_if again.  Why don't you do that later, matt?
@hostlist.each do |name|
	validhost = json_object["results"]["#{name}"]
	if validhost.has_key?("cnx_envtag")==false
		@hostlist.delete("#{name}")
	end	
end	
# now the good part, we loop through our host name and look for anything with a client of uhg.  Convert the project name to an option later
@hostlist.each do |name|
	if json_object["results"]["#{name}"]["cnx_client"]=="uhg"
		puts json_object["results"]["#{name}"]["cnx_envtag"]	
	end
end
