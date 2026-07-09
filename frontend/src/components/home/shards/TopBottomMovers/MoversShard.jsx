import useHoldings from "../Portfolio/Holdings/useHoldings"
import { testData } from './testData.js'


//cost_basis: 160.6
//​​current_value: 156.57
//​​gain_loss: -4.03
//​​gain_loss_pct: -2.51
//​​market_state: "REGULAR"
//​​name: "3M Company"
//​​shares: 1
//​​symbol: "MMM"
//​​todays_gain_loss: 1.87
//​​todays_gain_loss_pct: 1.21
//​​total_cost: 160.6
//​​unit_price: 156.57
// [{}, ...]
function updateThresholdState(highGroup, lowGroup) {
    // Assumes all members of high group are objects with a member '​​todays_gain_loss_pct'
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
    //const { loading, data, error } = useHoldings();
    const data = testData;

    let highGroup = [];
    let lowGroup = [];
    if (data) {
        let highGroupThreshold = 0;
        let highGroupThresholdIndex = null;

        let lowGroupThreshold = 0;
        let lowGroupThresholdIndex = null;

        [highGroupThreshold, highGroupThresholdIndex, lowGroupThreshold, lowGroupThresholdIndex] = updateThresholdState(highGroup, lowGroup);
        for (const company of data) {
            const todaysChangePct = Number(company.todays_gain_loss_pct);
            if (todaysChangePct > highGroupThreshold) {
                if (highGroup.length < 3) {
                    highGroup.push(company);
                } else {
                    highGroup.pop(highGroupThresholdIndex);
                    highGroup.push(company);
                };
            };
            if (todaysChangePct < lowGroupThreshold) {
                if (lowGroup.length < 3) {
                    lowGroup.push(company);
                } else {
                    lowGroup.pop(lowGroupThresholdIndex);
                    lowGroup.push(company);
                };
            };
        }
    };
    console.log('high group');
    console.log(highGroup);
    console.log('low group');
    console.log(lowGroup);
    return (
        <>
            <span> TEST </span>
        </>
    )
}