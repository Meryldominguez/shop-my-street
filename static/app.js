/** processForm: get data from form and make AJAX call to our API. */

async function processForm(evt) {
    evt.preventDefault();
    
    let formData= $("#searchform").serialize()
    console.log(formData)
    let response = await axios.post('/api/search', formData);

    console.log(response.data)
    return handleResponse(response.data)
}

/** handleResponse: deal with response from our lucky-num API. */

function handleResponse(resp) {
    $("#searchform input").empty()
    if(!resp["errors"]){
        
        for(let bus of resp){
            bus= JSON.parse(bus)
            console.log(bus)
            $("#search-results").append(`
            <div class="card bg-light mb-3" style="max-width: 20rem;">
                <div id="${bus.yelp_id}"class="card-header"><h4 style="display:inline" >${bus["name"]}</h4> <smaller class= "float-right">Rating: ${bus.rating}</smaller>
                <h6>${bus.categories.join('/')}</h6></div>
                <div class="card-body">
                <h5 class="card-title">${bus.address[0]}<br>${bus.address[1]}
                </h5>
                <h6>${bus.phone}</h6>

              <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
              <form action="/business/${bus.id}">
              <button>Details</>
              </form>
            </div>
          </div>`)}
        }
    
    else{
        for(let cat in resp.errors){
            console.log(resp.errors)
            $("#search-results").append(
                `<div class="alert alert-warning" role="alert">${cat}</div>`)
        }
    }

}


$("#searchform").on("submit", async(evt)=>{
    evt.preventDefault();
    $("#search-results").empty()
    response = await processForm(evt)
    return handleResponse(response)
});

//https://medium.com/@doobeh/posting-a-wtform-via-ajax-with-flask-b977782edeee
// $.ajaxSetup({
//     beforeSend: function(xhr, settings) {
//         if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
//             xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
//         }
//     }
// })
$(".disc-form").on("submit", async(evt)=>{

    evt.preventDefault();
    resp= await axios.post(`http://127.0.0.1:5000/discovery/${evt.target.id}`)

    return resp
})


// UTILS

function goBack() {
    window.history.back();
  }