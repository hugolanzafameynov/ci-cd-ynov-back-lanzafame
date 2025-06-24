const User = require("../model/user");
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const getAllUsers = async (req, res, next) => {
    try {
        // Exclure le mot de passe dans la réponse
        const users = await User.find({}, '-password');
        return res.status(200).json({ utilisateurs: users });
    } catch (error) {
        console.error(error);
        return next(error);
    }
};

const deleteUser = async (req, res, next) => {
    try {
        const { id } = req.params;
        // L'admin ne peut pas se supprimer lui-même
        if (req.user && req.user._id.toString() === id) {
            return res.status(403).json({ message: "Vous ne pouvez pas vous supprimer vous-même." });
        }
        const deletedUser = await User.findByIdAndDelete(id);
        if (!deletedUser) {
            return res.status(404).json({ message: "Utilisateur non trouvé." });
        }
        return res.status(200).json({ message: "Utilisateur supprimé." });
    } catch (error) {
        return next(error);
    }
};

const login = async (req, res, next) => {
    try {
        const { username, password } = req.body;
        const user = await User.findOne({ username });
        if (!user) {
            return res.status(401).json({ message: "Utilisateur non trouvé" });
        }
        const valid = await bcrypt.compare(password, user.password);
        if (!valid) {
            return res.status(401).json({ message: "Mot de passe incorrect" });
        }
        // Générer un token JWT
        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'secret', { expiresIn: '1d' });
        return res.status(200).json({ message: "Connexion réussie", token, user: { _id: user._id, username: user.username, role: user.role } });
    } catch (error) {
        return next(error);
    }
};

const addUser = async (req, res, next) => {
    try {
        const { username, password, role, name, lastName } = req.body;
        if (!username || !password) {
            return res.status(400).json({ message: "Username et password sont requis" });
        }
        const exists = await User.findOne({ username });
        if (exists) {
            return res.status(409).json({ message: "Ce nom d'utilisateur existe déjà" });
        }
        const user = new User({
            username,
            password,
            role: role || 'user',
            name,
            lastName
        });
        await user.save();
        return res.status(201).json({ message: "Utilisateur créé", user: { _id: user._id, username: user.username, role: user.role, name: user.name, lastName: user.lastName } });
    } catch (error) {
        return next(error);
    }
};

module.exports = { getAllUsers, deleteUser, login, addUser };
