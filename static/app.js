/** processForm: get data from form and make AJAX call to our API. */

/** Process the form data and make an API req.
 * @param {Event} evt used to preventDefault
 */
async function processForm(evt) {
  evt.preventDefault();

  const formData= $('#searchform').serialize();
  const response = await axios.post('/api/search', formData);

  return handleResponse(response.data);
}
/**
 * @param {*} arr array of category objects {name,term}
 * @return {list} string of category names, joined with a ', '
 */
function formatCategories(arr) {
  let list = arr.map((cat) => cat['name']);
  list= list.join(', ');
  return list;
}

// eslint-disable-next-line require-jsdoc
function handleResponse(resp) {
  $('#searchform input').empty();
  if (!resp.errors) {
    if (resp.length=== 0) {
      $('#search-results').append(
          `<div class="alert alert-warning" role="alert">
            There were no results in your area! Try again! 
            </div>`);
    } else {
      for (let bus of resp) {
        bus= JSON.parse(bus);
        $('#search-results').append(
            `<div class="card bg-light mb-3" 
            style="min-width: 20rem;max-width: 20rem;">
                <div id="${bus.yelp_id}"class="card-header">
                    <h4 style="display:inline">
                    ${bus['name']}
                    </h4> 
                    <smaller class= "float-right">
                    <img src="/static/small/${bus.rating}.png">
                    </smaller>
                    <h6>
                    ${formatCategories(bus.categories)}</h6>
                </div>
                <div class="card-body">
                    <h5 class="card-title">
                    ${bus.address[0] ? bus.address[0]: null}
                    <br>
                    ${bus.address[1]? bus.address[1]: null}
                    </h5>
                <h6>${bus.phone}</h6>

              <p class="card-text">
                <img class="" src="${bus.pic}"
                style="width: 200px; height: 200px" 
                alt="an image of ${bus.name}" class="img-thumbnail img">
              </p>
              <form action="/business/${bus.id}">
              <button class="btn btn-outline-secondary">More Info</>
              </form>
            </div>
          </div>`);
      }
    }
  } else {
    for (const cat in resp.errors) {
      if (resp.errors) {
        $('#search-results').append(
            `<div class="alert alert-warning" role="alert">${cat}</div>`);
      }
    }
  }
}


$('#searchform').on('submit', async (evt)=>{
  evt.preventDefault();
  $('#search-results').empty();
  const response = await processForm(evt);
  return handleResponse(response);
});

$('.disc-form').on('submit', async (evt)=>{
  evt.preventDefault();
  const resp= await axios.post(`/discovery/${evt.target.id}`);
  return resp;
});


// UTILS


/**
 * Return to the previous window
 * @param {int} num number of windows to go back
**/
function goBack(num) {
  window.history.go(-num);
}

$(function() {
  $('[data-toggle="tooltip"]').tooltip({
    animated: 'fade',
    html: true,
  });
});
