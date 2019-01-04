import numpy
from numpy.linalg import solve
from sklearn.metrics import mean_squared_error as mse


class ExplicitMF():
    def __init__(self, ratings, iterations=[10], n_factors=40, item_reg=0.0, user_reg=0.0, verbose=False):
        """
        Train a matrix factorization model to predict all empty entries in a matrix.
        The terminology assumes a ratings matrix which is ~ USER x ITEM
        
        Params
        ======
        ratings : (ndarray)
            User x Item matrix with corresponding ratings
        
        n_factors : (int)
            Number of latent factors (to assume) in factorization model
        
        item_reg : (float)
            Regularization term for item latent factors
        
        user_reg : (float)
            Regularization term for user latent factors
        
        verbose : (bool)
            Whether or not to printout training progress
        """
        
        self.ratings = ratings
        self.n_users, self.n_items = ratings.shape
        self.n_factors = n_factors
        self.item_reg = item_reg
        self.user_reg = user_reg
        self.iterations = iterations
        self._v = verbose


    def als_step(self, latent_vectors, fixed_vecs, ratings, _lambda, type='user'):
        """ One of two ALS steps. Solve for the latent vectors specified by type. """

        if type == 'user':
            # Precompute
            YTY = fixed_vecs.T.dot(fixed_vecs)
            lambdaI = numpy.eye(YTY.shape[0]) * _lambda
            for u in range(latent_vectors.shape[0]):
                latent_vectors[u, :] = solve((YTY + lambdaI), ratings[u, :].dot(fixed_vecs))
        
        elif type == 'item':
            # Precompute
            XTX = fixed_vecs.T.dot(fixed_vecs)
            lambdaI = numpy.eye(XTX.shape[0]) * _lambda
            for i in range(latent_vectors.shape[0]):
                latent_vectors[i, :] = solve((XTX + lambdaI), ratings[:, i].T.dot(fixed_vecs))

        return latent_vectors

    
    
    def train(self, n_iter = 10):
        """ Train model for n_iter iterations from scratch."""
        # initialize latent vectors
        self.user_vecs = numpy.random.random((self.n_users, self.n_factors))
        self.item_vecs = numpy.random.random((self.n_items, self.n_factors))        
        self.partial_train(n_iter)

        
    
    def partial_train(self, n_iter):
        """ Train model for n_iter iterations. Can be called multiple times for further training. """
        while (n_iter):
            if (self._v): print('\titerations left: {}'.format(n_iter))
            self.user_vecs = self.als_step(self.user_vecs, self.item_vecs, self.ratings, self.user_reg, type='user')
            self.item_vecs = self.als_step(self.item_vecs, self.user_vecs, self.ratings, self.item_reg, type='item')
            n_iter = n_iter - 1
    
    
    
    def predict_all(self):
        """ Predict ratings for every user and item. """
        predictions = numpy.zeros((self.user_vecs.shape[0], self.item_vecs.shape[0]))
        for u in range(self.user_vecs.shape[0]):
            for i in range(self.item_vecs.shape[0]):
                predictions[u, i] = self.predict(u, i)
                
        return predictions
    
    
    
    def predict(self, u, i):
        """ Single user and item prediction. """
        return self.user_vecs[u, :].dot(self.item_vecs[i, :].T)
    
    
    
    def calculate_learning_curve(self, test_matrix):
        """
        Track MSE as a function of training iterations.
        
        Params
        ======
        test : (2D ndarray)
            Testing dataset (assumed to be USER x ITEM).
        
        The function creates two new class attributes:
        
        train_mse : (list)
            Training data MSE values for each value of iterations
        test_mse : (list)
            Test data MSE values for each value of iterations
        """

        print ("Calculate learning curve")

        self.iterations.sort()
        self.train_mse = []
        self.test_mse  = []
        iter_diff = 0

        for (i, n_iter) in enumerate(self.iterations):
            if (self._v): print('Iteration: {}'.format(n_iter))
            if i == 0:
                #if self._v: print('i = 0; train({})'.format(n_iter - iter_diff))
                self.train(n_iter - iter_diff)
            else:
                #if self._v: print('partial_train({})'.format(n_iter - iter_diff))
                self.partial_train(n_iter - iter_diff)

            predictions = self.predict_all()

            self.train_mse += [self.get_mse(predictions, self.ratings)]
            self.test_mse  += [self.get_mse(predictions, test_matrix)]
            if (self._v):
                print('Train mse: ' + str(self.train_mse[-1]))
                print('Test mse:  ' + str(self.test_mse[-1]))
            iter_diff = n_iter

            

    def get_mse(self, pred, actual):
        # calc MSE (true ratings - predicted)^2
        pred   = pred[actual.nonzero()].flatten()
        actual = actual[actual.nonzero()].flatten()
        return mse(pred, actual)