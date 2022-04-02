// clang++ -o g ground_client.cpp
// clang++ -lcurl -o g ground_client.cpp
// gcc -lcurl -std=c++11 -o ground_client ground_client.cpp
#include <iostream>
#include <curl/curl.h>
#include <string>
#include <cstring>
#include "json.hpp"
#include "ground_client_classes.h"
/*
export CPLUS_INCLUDE_PATH="${CPLUS_INCLUDE_PATH:+${CPLUS_INCLUDE_PATH}:}<dir>"
#include "path/json.hpp"
*/
// export CPLUS_INCLUDE_PATH="${CPLUS_INCLUDE_PATH:+${CPLUS_INCLUDE_PATH}:}/opt/homebrew/opt/nlohmann-json"
// for convenience
using json = nlohmann::json;
using namespace std;

int main(){
    static const char *test = "test";
    CURL* curl;
    CURLcode res;
    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    curl_easy_setopt(curl, CURLOPT_URL, "localhost:3000/ping");
    curl_easy_setopt(curl, CURLOPT_HTTPGET, 1L);
    
    //curl_easy_setopt(curl, CURLOPT_URL, "localhost:3000/drone/telemetry");
    //curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "{\"hi\" : \"there\"}");
    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);
    /* Check for errors */
    if(res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s\n",
              curl_easy_strerror(res));
 
    /* always cleanup */
    curl_easy_cleanup(curl);

    return 0;
}

Telemetry getTelemetry(){
  CURL* curl;
  CURLcode res;
  string pong;
  curl_global_init(CURL_GLOBAL_ALL);
  curl = curl_easy_init();
  curl_easy_setopt(curl, CURLOPT_URL, "localhost:3000/ping");
  curl_easy_setopt(curl, CURLOPT_HTTPGET, 1L);
  //curl_easy_setopt(curl, CURLOPT_READDATA, &pong);
  res = curl_easy_perform(curl);
  /* Check for errors */
  if(res != CURLE_OK)
    fprintf(stderr, "curl_easy_perform() failed: %s\n",
            curl_easy_strerror(res));

  /* always cleanup */
  curl_easy_cleanup(curl);

  //cout << "var: " << pong << endl;
  cout << "test" << endl;
}

