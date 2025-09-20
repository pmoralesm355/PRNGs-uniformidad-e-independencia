import os
import matplotlib.pyplot as plt

def save_hist(samples, out_path, bins=50, title=None):
    plt.figure()
    plt.hist(samples, bins=bins, density=True, edgecolor='black')
    if title:
        plt.title(title)
    plt.xlabel('Valor')
    plt.ylabel('Densidad')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
