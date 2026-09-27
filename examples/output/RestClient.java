package com.qa.client;

import org.apache.http.client.methods.*;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import com.qa.base.TestBase;
import java.util.HashMap;

// Hand-written framework layer - wraps Apache HttpClient. Stable; not regenerated.
public class RestClient {
    public CloseableHttpResponse post(String url, String body, HashMap<String,String> headers) throws Exception {
        CloseableHttpClient client = HttpClients.createDefault();
        HttpPost post = new HttpPost(TestBase.BASE_URL + url);
        for (var e : headers.entrySet()) post.addHeader(e.getKey(), e.getValue());
        post.setEntity(new StringEntity(body));
        return client.execute(post);
    }
    public CloseableHttpResponse get(String url) throws Exception {
        CloseableHttpClient client = HttpClients.createDefault();
        return client.execute(new HttpGet(TestBase.BASE_URL + url));
    }
}
