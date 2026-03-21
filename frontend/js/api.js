const API_BASE = 'http://YOUR-EC2-PUBLIC-IP:5000/api';
// Change above to your actual backend URL after deployment

const Api = {
  _headers() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  },

  async request(method, path, body = null) {
    try {
      const opts = { method, headers: this._headers() };
      if (body) opts.body = JSON.stringify(body);
      const res  = await fetch(`${API_BASE}${path}`, opts);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Request failed');
      return data;
    } catch (err) {
      throw err;
    }
  },

  get:    (path)       => Api.request('GET',    path),
  post:   (path, body) => Api.request('POST',   path, body),
  put:    (path, body) => Api.request('PUT',    path, body),
  delete: (path)       => Api.request('DELETE', path),

  // Auth
  companyRegister: (d)  => Api.post('/auth/company/register', d),
  companyLogin:    (d)  => Api.post('/auth/company/login', d),
  userRegister:    (d)  => Api.post('/auth/user/register', d),
  userLogin:       (d)  => Api.post('/auth/user/login', d),

  // Interviews
  getInterviews:       ()    => Api.get('/interviews/'),
  getInterview:        (id)  => Api.get(`/interviews/${id}`),
  postInterview:       (d)   => Api.post('/interviews/', d),
  getCompanyInterviews:()    => Api.get('/interviews/company/mine'),
  closeInterview:      (id)  => Api.put(`/interviews/${id}/close`),

  // Bookings
  book:              (d)   => Api.post('/bookings/', d),
  myBookings:        ()    => Api.get('/bookings/my'),
  cancelBooking:     (id)  => Api.put(`/bookings/${id}/cancel`),
  interviewBookings: (id)  => Api.get(`/bookings/interview/${id}`),

  // Mock Interview
  mockChat: (messages) => Api.post('/mock/chat', { messages }),
};