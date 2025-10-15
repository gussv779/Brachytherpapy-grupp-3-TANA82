import cvxpy as cp


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