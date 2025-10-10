import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt

def lpm_calculations(dij, df_dose_intervall, P):
    structure_params = {
        row.StructureID: {
            "L": row.Lower,
            "U": row.Upper,
            "wL": row["Lower Penalty"],
            "wU": row["Upper Penalty"],
        }
        for _, row in df_dose_intervall.iterrows()
    }

    # the number of dose points and dwell points. basically len(P) len(J)
    nP, nJ = dij.shape

    t = cp.Variable(nJ, nonneg=True)  # dwell times for each dwell point
    xL = cp.Variable(nP, nonneg=True)  # underdose penalties (xli)
    xU = cp.Variable(nP, nonneg=True)  # overdose penalties (xui)

    constraints = []
    objective_terms = []

    #We're basically looping through each structure so that we can adjust the intervalls and penalties accordingly
    for s_id, params in structure_params.items():
        # Select points belonging to the specified structure
        idx = P.index[P["StructureID"] == s_id]
        if len(idx) == 0:
            continue

        #here we're setting the penalties and such so that it is only valued for this specific structure
        Ls, Us = params["L"], params["U"]
        wL, wU = params["wL"], params["wU"]

        # get all the relevant dij values based on idx, dji e idx
        d_sub = dij.loc[idx].to_numpy()
        dose_sum_over_time = d_sub @ t

        # Add constraints
        constraints += [
            # these are the same as the definitions as for xls and xus
            dose_sum_over_time >= Ls - xL[idx],
            dose_sum_over_time <= Us + xU[idx]
        ]


        # here we're summing up the s∈Swlsi∈Psxli+s∈Swusi∈Psxu
        objective_terms.append(wL * cp.sum(xL[idx]) + wU * cp.sum(xU[idx]))

    # Combine everything for each structure
    objective = cp.Minimize(cp.sum(objective_terms))
    prob = cp.Problem(objective, constraints)
    prob.solve()
    Dose_opt = dij.to_numpy() @ t.value

    return t.value, Dose_opt

def plot_LPM_curve(Ls, Us, wL, wU, Dose_opt=None, structure_name=None):
    doses = np.linspace(0.8*Ls, 1.2*Us, 400)
    xL = np.maximum(Ls - doses, 0)
    xU = np.maximum(doses - Us, 0)
    total_penalty = wL * xL + wU * xU

    plt.figure(figsize=(7,4))
    plt.plot(doses, total_penalty, 'k-', lw=2, label="Penalty function")
    plt.axvline(Ls, color="gray", linestyle=":", label="L$^s$")
    plt.axvline(Us, color="gray", linestyle="--", label="U$^s$")

    if Dose_opt is not None:
        plt.scatter(Dose_opt, np.zeros_like(Dose_opt),
                    color="red", alpha=0.6, label="Optimized doses")

    plt.xlabel("Delivered dose (cGy)")
    plt.ylabel("Penalty")
    title = f"LPM Penalty Curve"
    if structure_name:
        title += f" — {structure_name}"
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()
