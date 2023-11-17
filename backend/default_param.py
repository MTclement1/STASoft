# This file stocks default parameters for PEET.

BASE_PRM = ['\n', "fnVolume = {'path_to_mrc.mrc}\n",
            '\n', "fnModParticle = {'MTa_PtsAdded_Twisted.mod'}\n",
            '\n', "initMOTL = {'MTa_PtsAddedRefP55_initMOTL.csv'}\n",
            '\n', 'tiltRange = {[-56.18, 56.04]}\n',
            '\n', 'dPhi = {-9:3:9, -4.5:1.5:4.5, -2.3:1.1:2.3, -1:1:1}\n',
            '\n', 'dTheta = {-9:3:9, -4.5:1.5:4.5, -2.3:1.1:2.3, -1:1:1}\n',
            '\n', 'dPsi = {-9:3:9, -4.5:1.5:4.5, -2.3:1.1:2.3, -1:1:1}\n',
            '\n', 'searchRadius = {[6], [5], [3], [2]}\n',
            '\n', 'lowCutoff = {[0, 0.05], [0, 0.05], [0, 0.05], [0, 0.05]}\n',
            '\n', 'hiCutoff = {[0.1, 0.05], [0.1, 0.05], [0.1, 0.05], [0.1, 0.05]}\n',
            '\n', 'refThreshold = {110, 110, 110, 110}\n',
            '\n', 'duplicateShiftTolerance = [1, 1, 1, 1]\n',
            '\n', 'duplicateAngularTolerance = [1, 1, 1, 1]\n',
            '\n', 'reference = [1, 55]\n',
            '\n', "fnOutput = 'MTa'\n",
            '\n', 'szVol = [64, 64, 64]\n',
            '\n', "alignedBaseName = ''\n",
            '\n', 'debugLevel = 3\n',
            '\n', 'lstThresholds = [111:111:111]\n',
            '\n', 'refFlagAllTom = 1\n',
            '\n', 'lstFlagAllTom = 1\n',
            '\n', 'particlePerCPU = 5\n',
            '\n', 'yaxisType = 1\n',
            '\n', 'yaxisObjectNum = NaN\n',
            '\n', 'yaxisContourNum = NaN\n',
            '\n', 'flgWedgeWeight = 1\n',
            '\n', "sampleSphere = 'none'\n",
            '\n', 'sampleInterval = NaN\n',
            '\n', "maskType = 'cylinder'\n",
            '\n', 'maskModelPts = []\n',
            '\n', 'insideMaskRadius = 12\n',
            '\n', 'outsideMaskRadius = 28\n',
            '\n', 'nWeightGroup = 8\n',
            '\n', 'flgRemoveDuplicates = 0\n',
            '\n', 'flgAlignAverages = 1\n',
            '\n', 'flgFairReference = 0\n',
            '\n', 'flgAbsValue = 1\n',
            '\n', 'flgStrictSearchLimits = 1\n',
            '\n', 'flgNoReferenceRefinement = 0\n',
            '\n', 'flgRandomize = 0\n',
            '\n', 'cylinderHeight = 64\n',
            '\n', 'maskBlurStdDev = 2\n',
            '\n', 'flgVolNamesAreTemplates = 0\n',
            '\n', 'edgeShift = 0\n',
            '\n', 'excludeList = []\n',  # excludeList: A list of particle numbers to be excluded.
            '\n', 'includeList = []\n',  # includeList: A list of particle numbers to be included.
            '\n', 'flgElevationCompensation = 0\n',  # If 1 (default = 0), adjust correlation scores for variation
            # with elevation angle during particle selection.
            '\n', 'flgFRM = 1\n',  # flgFRM: If 1 (default) allow fast rotational matching when applicable.
            '\n', 'flgAllowMaskedCorrelation = 1\n',  # ff 1 (default = 0) use a slower cross-correlation calculation
            # which may be slightly more accurate when masking is in use.
            '\n', 'flgFilterRefOnly = 0\n',  # If 1 (default = 0), during alignment apply frequency filtration
            # to the reference only, rather than both reference and particles.
            '\n', 'flgSearchAlongParticleAxes = 0\n',  # If 1 (default = 0), search distances will be (approximately)
            # along particle rather than tomogram coordinates.
            '\n', 'flgFPWedgeMask = 0\n',  # flgFPWedgeMask: If 1 (default = 0), allow floating point wedge masks.
            '\n', 'yAxisSymmetry = []\n',  # yAxisSymmetry: A per iterations list of axial symmetry search orders.
            # Iterations with entries N > 1 will perform a rotation only search
            # about tomogram Y for axial symmetry.
            '\n', 'flgUseExtractedParticles = 0\n',  # Use previously extracted particles (rather than automatically
            # extracting on the fly).
            '\n', 'flgCNMasking = 1']  # flgCNMasking: If 1 (default), apply a spherical real-space mask during
# symmetric averaging.
