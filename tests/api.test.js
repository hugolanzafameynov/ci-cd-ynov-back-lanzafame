const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../server');
const User = require('../src/model/user');

describe('API Utilisateurs', () => {
  beforeAll(async () => {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(process.env.DATABASE_URL, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
      });
    }
  });

  beforeEach(async () => {
    await User.deleteMany({});
    const admin = new User({
      username: 'admin',
      password: 'admin123',
      role: 'admin'
    });
    await admin.save();
  });

  afterAll(async () => {
    await mongoose.disconnect();
  });

  describe('Authentification', () => {
    it('POST /v1/login doit renvoyer 200', async () => {
      const res = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'admin123' });
      expect(res.statusCode).toBe(200);
      if (res.statusCode === 200) {
        expect(res.body).toHaveProperty('token');
      }
    });
    it('POST /v1/login avec username inexistant doit renvoyer 401', async () => {
      const res = await request(app)
        .post('/v1/login')
        .send({ username: 'usernotexist', password: 'anypass' });
      expect(res.statusCode).toBe(401);
    });
    it('POST /v1/login avec mauvais mot de passe doit renvoyer 401', async () => {
      const res = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'wrongpass' });
      expect(res.statusCode).toBe(401);
    });
  });

  describe('Création d\'utilisateur', () => {
    it('POST /v1/users doit renvoyer 201', async () => {
      const uniqueUsername = `testuser_${Date.now()}`;
      const res = await request(app)
        .post('/v1/users')
        .send({ username: uniqueUsername, password: 'testpass', name: 'Test', lastName: 'User' });
      expect(res.statusCode).toBe(201);
    });
    it('POST /v1/users sans username doit renvoyer 400', async () => {
      const res = await request(app)
        .post('/v1/users')
        .send({ password: 'testpass' });
      expect(res.statusCode).toBe(400);
    });
    it('POST /v1/users sans password doit renvoyer 400', async () => {
      const res = await request(app)
        .post('/v1/users')
        .send({ username: 'usernopass' });
      expect(res.statusCode).toBe(400);
    });
    it('POST /v1/users ne doit jamais renvoyer le champ password', async () => {
      const res = await request(app)
        .post('/v1/users')
        .send({ username: 'nopassfield', password: 'nopass', name: 'No', lastName: 'Pass' });
      if (res.body.user) {
        expect(res.body.user).not.toHaveProperty('password');
      }
    });
    it('POST /v1/users avec utilisateur déjà existant doit renvoyer 409', async () => {
      // Crée un utilisateur
      await request(app)
        .post('/v1/users')
        .send({ username: 'duplicate', password: 'duplicatepass' });
      // Tente de créer le même utilisateur
      const res = await request(app)
        .post('/v1/users')
        .send({ username: 'duplicate', password: 'duplicatepass' });
      expect(res.statusCode).toBe(409);
    });
    it('POST /v1/users avec caractères spéciaux dans username doit fonctionner', async () => {
      const specialUsername = `user_${Date.now()}@test.com`;
      const res = await request(app)
        .post('/v1/users')
        .send({ username: specialUsername, password: 'testpass', name: 'Special', lastName: 'User' });
      expect(res.statusCode).toBe(201);
    });

  });

  describe('Récupération d\'utilisateurs', () => {
    it('GET /v1/users (non authentifié) doit renvoyer 401', async () => {
      const res = await request(app).get('/v1/users');
      expect(res.statusCode).toBe(401);
    });
    it('GET /v1/users avec token user non admin doit renvoyer 403', async () => {
      await request(app)
        .post('/v1/users')
        .send({ username: 'notadmin', password: 'notadminpass' });
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'notadmin', password: 'notadminpass' });
      const res = await request(app)
        .get('/v1/users')
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(403);
    });
    it('GET /v1/users avec token admin doit renvoyer 200 et la liste des utilisateurs', async () => {
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'admin123' });
      const res = await request(app)
        .get('/v1/users')
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('utilisateurs');
      expect(Array.isArray(res.body.utilisateurs)).toBe(true);
    });
    it('GET /v1/users ne doit jamais renvoyer les mots de passe', async () => {
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'admin123' });
      const res = await request(app)
        .get('/v1/users')
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(200);
      expect(res.body.utilisateurs).toBeDefined();
      res.body.utilisateurs.forEach(user => {
        expect(user).not.toHaveProperty('password');
      });
    });
  });

  describe('Suppression d\'utilisateur', () => {
    it('DELETE /v1/users/:id avec token admin doit supprimer un utilisateur', async () => {
      const createRes = await request(app)
        .post('/v1/users')
        .send({ username: 'todelete', password: 'todeletepass' });;
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'admin123' });
      const res = await request(app)
        .delete(`/v1/users/${createRes.body.user?._id}`)
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(200);
    });
    it('DELETE /v1/users/:id sans token doit renvoyer 401', async () => {
      const res = await request(app)
        .delete('/v1/users/507f1f77bcf86cd799439011'); // ID fictif
      expect(res.statusCode).toBe(401);
    });
    it('DELETE /v1/users/:id avec token user non admin doit renvoyer 403', async () => {
      await request(app)
        .post('/v1/users')
        .send({ username: 'notadmindelete', password: 'notadmindeletepass' });
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'notadmindelete', password: 'notadmindeletepass' });
      const res = await request(app)
        .delete('/v1/users/507f1f77bcf86cd799439011') // ID fictif
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(403);
    });
    it('DELETE /v1/users/:id avec utilisateur non existant doit renvoyer 404', async () => {
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'admin123' });
      const res = await request(app)
        .delete('/v1/users/507f1f77bcf86cd799439011') // ID fictif
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(404);
    });
    it('DELETE /v1/users/:id admin par lui-même doit renvoyer 403', async () => {
      const loginRes = await request(app)
        .post('/v1/login')
        .send({ username: 'admin', password: 'admin123' });
      const res = await request(app)
        .delete(`/v1/users/${loginRes.body.user._id}`)
        .set('Authorization', `Bearer ${loginRes.body.token}`);
      expect(res.statusCode).toBe(403);
    });
  });
});
