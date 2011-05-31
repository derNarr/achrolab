        # put xyY into R for the plotCalibration method
        xyY_x = robjects.FloatVector([x[0] for x in xyY_list])
        xyY_y = robjects.FloatVector([x[1] for x in xyY_list])
        xyY_Y = robjects.FloatVector([x[2] for x in xyY_list])
        R("xyY_x <- " + xyY_x.r_repr())
        R("xyY_y <- " + xyY_y.r_repr())
        R("xyY_Y <- " + xyY_Y.r_repr())

        # plot used datapoints for calibration
        R(' pdf("data_points_xyY_tubes'+time.strftime("%Y%m%d_%H%M")
            +'.pdf")')
        R('''
        layout(matrix(c(1,1,1,2,3,4), 3, 2), respect=matrix(c(0,0,0,1,1,1),3,2))
        
        par(mai=c(1.3, .5, 1, .1), mgp=c(2.2,1,0))
        plot(xyY_x[idr], xyY_y[idr], type="b", pch=16, col="red",
            ylim=c(0,.8), xlim=c(0,.8), xlab="x", ylab="y", main="xyY Space for
            Tubes", sub="Measured data points, which were used for
            calibration")
        points(xyY_x[idg], xyY_y[idg], type="b", pch=16, col="green")
        points(xyY_x[idb], xyY_y[idb], type="b", pch=16, col="blue")
        
        par(mai=c(.5, .5, 0.1, 0.1), mgp=c(2.2,1,0))
        plot(voltage_r[idr], xyY_Y[idr], type="l", pch=16, col="red",
            xlab="voltage red channel", ylab="Y", ylim=c(0,30))
        plot(voltage_g[idg], xyY_Y[idg], type="l", pch=16, col="green",
            xlab="voltage green channel", ylab="Y", ylim=c(0,30))
        plot(voltage_b[idb], xyY_Y[idb], type="l", pch=16, col="blue",
            xlab="voltage blue channel", ylab="Y", ylim=c(0,30))

        dev.off()
        ''')


