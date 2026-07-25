using System.Net;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;

namespace TravelPlannerFunctions.Functions;

public class HelloWorldApi
{
    [Function(nameof(HelloWorld))]
    public async Task<HttpResponseData> HelloWorld(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "hello")] HttpRequestData req)
    {
        var response = req.CreateResponse(HttpStatusCode.OK);
        await response.WriteStringAsync("Hello from TravelPlannerFunctions.");
        return response;
    }
}
