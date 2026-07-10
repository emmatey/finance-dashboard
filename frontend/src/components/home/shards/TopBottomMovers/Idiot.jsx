function updateThresholdState(highGroup, lowGroup) {
    let lowestValue = null;
    let lowIndex = null;
    if (highGroup.length > 0) {
        highGroup.forEach((company, index) => {
            const todaysChangePct = Number(company.todays_gain_loss_pct);
            if (lowIndex === null) {
                lowestValue = todaysChangePct;
                lowIndex = index;
            };
            if (todaysChangePct < lowestValue) {
                lowestValue = todaysChangePct;
                lowIndex = index;
            };
        });
    };
    let highestValue = null;
    let highIndex = null;
    if (lowGroup.length > 0) {
        lowGroup.forEach((company, index) => {
            const todaysChangePct = Number(company.todays_gain_loss_pct);
            if (highIndex === null) {
                highestValue = todaysChangePct;
                highIndex = index;
            };
            if (todaysChangePct > highestValue) {
                highestValue = todaysChangePct;
                highIndex = index;
            };
        });
    }
    return [lowestValue, lowIndex, highestValue, highIndex]
}

export default function MoversShard() {
    const { loading, data, error } = useHoldings();
    let highGroup = [];
    let lowGroup = [];

    if (data) {
        let highGroupThreshold = null;
        let highGroupThresholdIndex = null;

        let lowGroupThreshold = null;
        let lowGroupThresholdIndex = null;

        for (const company of data) {
            [highGroupThreshold, highGroupThresholdIndex, lowGroupThreshold, lowGroupThresholdIndex] = updateThresholdState(highGroup, lowGroup);
            const todaysChangePct = Number(company.todays_gain_loss_pct);

            // Prime the pump
            if ((highGroup.length < 3) && (todaysChangePct >= 0)) {
                highGroup.push(company);
                continue;
            };
            if ((lowGroup.length < 3) && (todaysChangePct < 0)) {
                lowGroup.push(company);
                continue;
            };

            if (todaysChangePct > highGroupThreshold) {
                highGroup.splice(highGroupThresholdIndex, 1);
                highGroup.push(company);
            } else if (todaysChangePct < lowGroupThreshold) {
                lowGroup.splice(lowGroupThresholdIndex, 1);
                lowGroup.push(company);
            };
        };
    };

    return (
        <>
        {'render high and low movers here.'}
        </>
    )
}
