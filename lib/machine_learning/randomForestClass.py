from joblib import load as joblib_load
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class RandForest:
    """
    A class used to represent a Random Forest model.

    Attributes
    ----------

    name : str
        The name of the model.
    model_dir : str
        The directory where the model is stored.

    Methods
    -------

    __init__(name, model_dir)
        Initializes the RandForest object with a model name and directory.
    
    _load_model_object()
        Loads the model object from the specified directory.
    
    predict_probability(accel_data, max_displacement)
        Predicts the probability of the input using the loaded model.
    
    plot_prediction(data, labels=['Class 1','Class 2','Class 3','Class 4'], title="", fig_size=[6, 4], save=None, name=None)
        Plots the prediction data.
    """
    def __init__(self, name, model_dir):
        """
        Initializes the RandForest object with a model name and directory.

        Parameters
        ----------

        name : str
            The name of the model.
        model_dir : str
            The directory where the model is stored.
        """
        # Store the model name
        self.name = name

        # Store the path to the model
        self.model_dir = model_dir
        
        # Load the model object
        self._load_model_object()

    def _load_model_object(self):
        """
        Loads the model object from the specified directory using joblib.

        Notes
        -----

        This method uses joblib's load function to load the model object. It may need to be updated if different 
        model loading mechanisms are required in the future.
        """
        # NOTE: In the future might need to use different load functions depending on the model type
        
        # Use joblib.load to load the model     
        self.model_obj = joblib_load(self.model_dir)

    def predict_probability(self, accel_data, max_displacement):
        """
        Predicts the probability of the input using the loaded model.

        Parameters
        ----------

        accel_data : array-like
            The acceleration data to be used for prediction.
        max_displacement : array-like
            The maximum displacement data to be used for prediction.

        Returns
        -------

        output : array
            The predicted probabilities for each class.

        Notes
        -----

        This method stacks the acceleration data and maximum displacement into a nested column array as expected 
        by the trained model and then uses the model's `predict_proba` method to generate predictions.
        """
        # Stack the data into a nested column arr (Expected input of the trained model)
        input = np.column_stack((accel_data, max_displacement))

        # Call the predict_proba module of the loaded machine learning object
        output = self.model_obj.predict_proba(input)

        return output

    @staticmethod
    def plot_prediction(data, labels= ['Class 1','Class 2','Class 3','Class 4'], title = "", fig_size = [6, 4], save=None, name = None):
        """
        Plots the prediction data.

        Parameters
        ----------
        
        data : array-like
            The prediction data to be plotted.
        labels : list of str, optional
            The labels for the classes (default is ['Class 1', 'Class 2', 'Class 3', 'Class 4']).
        title : str, optional
            The title of the plot (default is an empty string).
        fig_size : list of int, optional
            The size of the figure (default is [6, 4]).
        save : bool, optional
            Whether to save the plot as a file (default is None, which is equivalent to False).
        name : str, optional
            The filename to save the plot as (default is None, which is equivalent to 'output_class_plot').

        Notes
        -----

        This method creates a bar plot of the prediction data and optionally saves it to a file if `save` is True.
        The filename is determined by the `name` parameter.
        """

        if save is None:
            save = False
        
        if name is None:
            name = "output_class_plot"

        fig, axs = plt.subplots(ncols=1, nrows = 1, figsize = fig_size)
        # Plot the data
        axs.bar(labels, data)

        # If the title is something other than an empty string show the title
        if not title == "":
            axs.set_title(title)

        axs.set_xlabel("Classes")
        axs.set_ylabel("Predicted Probability")

        plt.tight_layout()
        if save:
            fig.savefig(name, dpi=300)

        plt.show()

if __name__ == "__main__":
    # Add some tests here
    pass